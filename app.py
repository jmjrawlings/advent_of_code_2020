from datetime import time
from enum import auto
from h2o_wave import Q, main, app, ui
from src import *
import altair as alt


def title(day: Day):
    return f"Day {day.num} - {day.title}"


class Tab(Enumeration):
    part_1 = auto()
    part_2 = auto()
    input = auto()


@attr.s
class State:
    day_num: int = attr.ib(default=1)
    part_num: int = attr.ib(default=1)
    engine: Engine = attr.ib(default=Engine.CHUFFED, converter=Engine.parse)
    threads: int = attr.ib(default=4)
    timeout: Duration = attr.ib(default=to_dur(seconds=10), converter=to_dur)
    tab: Tab = attr.ib(default=Tab.part_1, converter=Tab.parse)
    solving: bool = attr.ib(default=False)

    @property
    def day(self):
        return Day.s[self.day_num - 1]

    @property
    def part(self):
        if self.part_num == 1:
            return self.day.part_1
        else:
            return self.day.part_2


state = State()


async def render(q: Q, app: State):
    q.page.add(
        "days",
        ui.form_card(
            box="1 1 2 8",
            items=[
                ui.choice_group(
                    "day",
                    label="Advent of Code 2020",
                    choices=[ui.choice(name=d.num, label=title(d)) for d in Day.s],
                    trigger=True,
                    value=app.day_num,
                )
            ],
        ),
    )

    q.page.add(
        "solver",
        ui.form_card(
            "8 1 2 8",
            items=[
                ui.choice_group(
                    "engine",
                    label="Solver Engine",
                    choices=[ui.choice(name=e.name) for e in Engine],
                    value=app.engine.name,
                ),
                ui.separator(),
                ui.slider(
                    "threads",
                    label="Max CPU Theads",
                    min=1,
                    max=48,
                    value=app.threads,
                    step=1,
                ),
                ui.separator(),
                ui.slider(
                    "timeout",
                    label="Timeout (seconds)",
                    min=1,
                    max=60,
                    value=int(app.timeout.total_seconds()),
                    step=1,
                ),
                ui.separator(),
                ui.button("solve", "Run Solver"),
            ],
        ),
    )

    q.page.add(
        "tab",
        ui.tab_card(
            box="3 1 5 1",
            items=[ui.tab("part_1", "Part 1"), ui.tab("part_2", "Part 2")],
            value=app.tab.name,
        ),
    )
    c = (
        alt.Chart(alt.InlineData(values=[dict(x=1, y=1)]))
        .mark_line()
        .encode(x="x:Q", y="y:Q")
        .to_json()
    )
    q.page.add("form", ui.vega_card(box="3 2 5 7", title="Viz", specification=c))


async def sync(q, state: State):
    for k, v in (q.args.__kv or {}).items():
        log.debug(f"{k} = {v}")

    if q.args.day:
        state.day_num = q.args.day
    if q.args.part:
        state.part_num = q.args.part
    if q.args.engine:
        state.engine = q.args.engine
    if q.args.threads:
        state.threads = q.args.threads
    if q.args.timeout:
        state.timeout = q.args.timeout
    if q.args.part_1:
        state.tab = Tab.part_1
    elif q.args.part_2:
        state.tab = Tab.part_2

    if q.args.solve and not state.solving:
        state.solving = True
        answer = await state.part.solve()
        state.solving = False


@app("/app")
async def serve(q: Q):
    await sync(q, state)

    if not q.client.init:
        q.client.init = True
        await render(q, state)
        await q.page.save()
        return

    q.page["sidebar"].items[0].choice_group.value = state.day_num
    q.page["sidebar"].items[2].choice_group.value = state.part_num
    # q.page["tab"].items[0].text_xl.content = title(day)
    # q.page["tab"].items[1].choice_group.value = part.num

    await q.page.save()
