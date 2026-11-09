"""In-memory task lifecycle, ownership checks and quota accounting."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
from threading import Event, RLock
from uuid import uuid4

from ai_studio.permissions import UserContext
from ai_studio.providers import LocalImageProvider
from ai_studio.tools import LocalTools

USERS = {
    "local-member-key": UserContext("member", "user", "standard"),
    "local-admin-key": UserContext("admin", "admin", "professional"),
}
MODELS = [
    {"id": "local-poster", "name": "简约海报", "professional": False},
    {"id": "local-badge", "name": "紫色卡片", "professional": True},
]


class Runtime:
    def __init__(self, delay: float = .6):
        self.lock = RLock()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.runs = {}
        self.assets = {}
        self.stops = {}
        self.wallets = {user.user_id: {"available": 100, "reserved": 0, "spent": 0} for user in USERS.values()}
        self.delay = delay
        self.provider = LocalImageProvider()
        self.tools = LocalTools()

    def close(self):
        with self.lock:
            for run_id, stop in self.stops.items():
                stop.set()
                self._finish(self.runs[run_id], "canceled")
        self.executor.shutdown(wait=True)

    def profile(self, user):
        with self.lock:
            return {"user_id": user.user_id, "role": user.role, "user_type": user.user_type, "credits": dict(self.wallets[user.user_id])}

    def models(self, user):
        return [model for model in MODELS if not model["professional"] or user.user_type == "professional"]

    def _owned(self, user, run_id):
        run = self.runs.get(run_id)
        if run is None:
            raise LookupError("任务不存在")
        if user.role != "admin" and run["user_id"] != user.user_id:
            raise PermissionError("无权查看或修改该任务")
        return run

    def list_runs(self, user):
        with self.lock:
            return [deepcopy(run) for run in reversed(list(self.runs.values())) if user.role == "admin" or run["user_id"] == user.user_id]

    def get(self, user, run_id):
        with self.lock:
            return deepcopy(self._owned(user, run_id))

    def _event(self, run, state):
        run["state"] = state
        run["events"].append({"state": state, "at": datetime.now(timezone.utc).isoformat()})

    def create(self, user, kind, target, prompt):
        if not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= 500:
            raise ValueError("请输入 1 到 500 个字符")
        if kind == "image":
            if target not in {model["id"] for model in MODELS}:
                raise ValueError("未知模型")
            if target not in {model["id"] for model in self.models(user)}:
                raise PermissionError("当前用户类型不能使用该模型")
        elif kind == "tool":
            if target not in {tool.name for tool in self.tools.list_tools()}:
                raise ValueError("未知工具")
        else:
            raise ValueError("未知任务类型")
        cost = 2 if kind == "image" else 1
        with self.lock:
            wallet = self.wallets[user.user_id]
            if wallet["available"] < cost:
                raise ValueError("本地额度不足")
            run_id = uuid4().hex
            wallet["available"] -= cost
            wallet["reserved"] += cost
            run = {"id": run_id, "user_id": user.user_id, "kind": kind, "target": target, "prompt": prompt.strip(), "cost": cost, "events": [], "asset_id": None, "result": None, "error": None}
            self._event(run, "queued")
            self.runs[run_id] = run
            self.stops[run_id] = Event()
            snapshot = deepcopy(run)
            try:
                self.executor.submit(self._execute, run_id)
            except RuntimeError:
                self._finish(run, "failed", error="任务执行器已关闭")
                raise ValueError("任务执行器已关闭")
            return snapshot

    def _finish(self, run, state, result=None, image=None, error=None):
        if run["state"] in {"completed", "failed", "canceled"}:
            return
        wallet = self.wallets[run["user_id"]]
        wallet["reserved"] -= run["cost"]
        if state == "completed":
            wallet["spent"] += run["cost"]
            if image is not None:
                asset_id = uuid4().hex
                self.assets[asset_id] = {"run_id": run["id"], "content": image}
                run["asset_id"] = asset_id
            run["result"] = result
        else:
            wallet["available"] += run["cost"]
        run["error"] = error
        self._event(run, state)

    def _execute(self, run_id):
        stop = self.stops[run_id]
        if stop.wait(self.delay):
            return
        with self.lock:
            run = self.runs[run_id]
            if run["state"] != "queued":
                return
            self._event(run, "running")
        if stop.wait(self.delay):
            return
        try:
            if run["kind"] == "image":
                image = self.provider.render(run["target"], run["prompt"])
                result = {"provider": "local-svg", "media_type": "image/svg+xml"}
            else:
                image = None
                result = self.tools.execute(run["target"], run["prompt"])
            with self.lock:
                self._finish(run, "completed", result=result, image=image)
        except Exception:
            with self.lock:
                self._finish(run, "failed", error="任务执行失败，预占额度已释放")

    def cancel(self, user, run_id):
        with self.lock:
            run = self._owned(user, run_id)
            if run["state"] not in {"queued", "running"}:
                raise ValueError("任务已结束，不能取消")
            self.stops[run_id].set()
            self._finish(run, "canceled")
            return deepcopy(run)

    def asset(self, user, asset_id):
        with self.lock:
            asset = self.assets.get(asset_id)
            if asset is None:
                raise LookupError("素材不存在")
            self._owned(user, asset["run_id"])
            return asset["content"]
