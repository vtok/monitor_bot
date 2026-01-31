import asyncio
import subprocess
import time
from datetime import timedelta

from bot.constants import PING_INTERVAL, STATE_CONFIRMATION

LIGHT_ON = True
LIGHT_OFF = False


def fmt_duration(seconds: float) -> str:
    return str(timedelta(seconds=int(seconds)))


class PingMonitor:
    def __init__(self, name: str, target_ip: str):
        self.name = name
        self.target_ip = target_ip

        self.initialized = False

        # Confirmed state (unknown until the first confirmation)
        self.current_state: bool | None = None
        self.state_start_ts: float | None = None

        # Candidate for confirmation
        self.pending_state: bool | None = None
        self.pending_since: float | None = None

        # Statistics
        self.total_up = 0.0
        self.total_down = 0.0

    def ping(self) -> bool:
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", self.target_ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return LIGHT_ON if result.returncode == 0 else LIGHT_OFF
        except Exception:
            return LIGHT_OFF

    def build_state_message(
            self,
            new_state: bool,
            now: float,
            initial: bool = False,
    ) -> str:
        msg: list[str] = []

        # ================= INITIAL STATE =================
        if initial:
            self.current_state = new_state
            self.state_start_ts = now

            msg.append(f"ℹ️ Початковий стан: {self.name}")
            msg.append("")

            if new_state is LIGHT_ON:
                msg.append("🟢 Є світло")
            else:
                msg.append("🔴 Немає світла")

            return "\n".join(msg)

        # ================= STATE CHANGE =================
        if self.current_state is None or self.state_start_ts is None:
            # захист на дуже рідкісний edge-case
            self.current_state = new_state
            self.state_start_ts = now
            return ""

        previous_state = self.current_state
        previous_duration = now - self.state_start_ts

        if previous_state is LIGHT_ON:
            self.total_up += previous_duration
        else:
            self.total_down += previous_duration

        self.current_state = new_state
        self.state_start_ts = now


        if new_state is LIGHT_ON:
            msg.append(f"✅ Дали світло ({self.name})")
        else:
            msg.append(f"🚨 Зникло світло ({self.name})")

        msg.append("")

        prev_text = "увімкнене" if previous_state is LIGHT_ON else "відсутнє"
        msg.append(
            f"⏱️ Світло було {prev_text}: {fmt_duration(previous_duration)}"
        )

        msg.append("")
        msg.append("📊 Загальна статистика:")
        msg.append(f"🟢 Зі світлом:  {fmt_duration(self.total_up)}")
        msg.append(f"🔴 Без світла:  {fmt_duration(self.total_down)}")

        return "\n".join(msg)

    async def run(self, notify_callback):
        while True:
            now = time.time()
            detected_state = self.ping()

            if self.pending_state is None:
                self.pending_state = detected_state
                self.pending_since = now
                await asyncio.sleep(PING_INTERVAL)
                continue

            if detected_state != self.pending_state:
                self.pending_state = detected_state
                self.pending_since = now
            else:
                if self.pending_since is not None and now - self.pending_since >= STATE_CONFIRMATION:
                    if not self.initialized:
                        msg = self.build_state_message(self.pending_state, now, initial=True)
                        await notify_callback(self.name, msg)
                        self.initialized = True
                    elif self.pending_state != self.current_state:
                        msg = self.build_state_message(self.pending_state, now)
                        await notify_callback(self.name, msg)

            await asyncio.sleep(PING_INTERVAL)

    def get_status(self) -> str:
        if self.current_state is None or self.state_start_ts is None:
            return f"ℹ️ {self.name}: стан ще не визначений, зачекай кілька секунд…"

        now = time.time()
        current_duration = now - self.state_start_ts

        up = self.total_up
        down = self.total_down

        if self.current_state is LIGHT_ON:
            up += current_duration
        else:
            down += current_duration

        state_text = "Є світло" if self.current_state is LIGHT_ON else "Немає світла"
        state_icon = "🟢" if self.current_state is LIGHT_ON else "🔴"

        return (
            f"💡 {self.name}\n\n"
            f"{state_icon} ЗАРАЗ: {state_text}\n"
            f"⏱ Триває: {fmt_duration(current_duration)}\n\n"
            f"📊 Всього зі світлом:  {fmt_duration(up)}\n"
            f"📊 Всього без світла: {fmt_duration(down)}"
        )
