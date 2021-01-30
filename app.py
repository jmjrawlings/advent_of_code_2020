from enum import auto
from os import sep
from h2o_wave import Q, main, app, ui
from src import *
import altair as alt
from asyncio import Future


def title(day: Day):
    return f"Day {day.num} - {day.title}"


class Tab(Enumeration):
    part_1 = auto()
    part_2 = auto()
    input = auto()


@attr.s
class State(Base):

    # fmt:off
    init    : bool      = attr.ib(default=False)
    day_num : int       = attr.ib(default=1)
    part_num: int       = attr.ib(default=1)
    opts    : SolveOpts = attr.ib(factory = SolveOpts)
    tab     : Tab       = attr.ib(default=Tab.part_1, converter=Tab.parse) # type:ignore
    solving : bool      = attr.ib(default=False)
    answer  : int       = attr.ib(default=0)
    solve   : Optional[Future[None]] = attr.ib(default=None)
    # fmt:on

    @property
    def day(self):
        return Day.s[self.day_num - 1]

    @property
    def part(self):
        if self.part_num == 1:
            return self.day.part_1
        else:
            return self.day.part_2


def log_args(q: Q):
    for k, v in q.args.__dict__["__kv"].items():
        log.debug(f"arg {k}:{type(v).__name__} = {v}")


def log_app(app: State):
    for k, v in app.__dict__.items():
        log.info(f"app {k}:{type(v).__name__} = {v}")


state = State()


async def render(q: Q, app: State):
    if app.init:
        return

    app.init = True

    q.page.add(
        "header",
        ui.header_card(
            # Place card in the header zone, regardless of viewport size.
            box="1 1 8 1",
            title="Advent of Code 2020",
            subtitle="Solution browser and interactive playground",
            nav=[
                ui.nav_group(
                    "Days",
                    collapsed=False,
                    items=[ui.nav_item(d.num, f"{d.num} - {d.title}") for d in Day.s],
                ),
                ui.nav_group(
                    "Settings",
                    items=[
                        ui.nav_item(name="#about", label="About"),
                        ui.nav_item(name="#support", label="Support"),
                    ],
                ),
            ],
        ),
    )

    q.page.add(
        "settings",
        ui.form_card(
            "1 2 2 7",
            items=[
                ui.choice_group(
                    "part",
                    label="Part",
                    choices=[
                        ui.choice(1, "Part 1"),
                        ui.choice(2, "Part 2"),
                    ],
                    trigger=True,
                    value=app.day_num,
                ),
                ui.separator(),
                ui.choice_group(
                    "engine",
                    label="Solver Engine",
                    choices=[ui.choice(name=e.name) for e in Engine],
                    value=app.opts.engine.name,
                ),
                ui.separator(),
                ui.slider(
                    "processes",
                    label="Max Processes",
                    min=1,
                    max=48,
                    value=app.opts.processes,
                    step=1,
                    tooltip="The maximum number of processes to use.  Only applicable for certain solver engines.",
                ),
                ui.separator(),
                ui.slider(
                    "timeout",
                    label="Timeout (seconds)",
                    min=1,
                    max=60,
                    value=int(app.opts.timeout.total_seconds()),
                    step=1,
                    tooltip="The maximum amount of time the solver will run for before terminating.",
                ),
                ui.separator(),
                ui.button("solve", "Run Solver"),
            ],
        ),
    )

    c = (
        alt.Chart(alt.InlineData(values=[dict(x=1, y=1)]))
        .mark_line()
        .encode(x="x:Q", y="y:Q")
        .properties(width="container", height="container")
        .interactive()
        .to_json()
    )
    q.page.add("form", ui.vega_card(box="3 2 5 3", title="Viz", specification=c))
    await q.page.save()


async def solvex(q: Q, state: State, debounce=100):

    lines = list(state.day.lines)
    data = state.day.data(lines)
    model = state.part.formulate(data)
    last = Solution()

    async for sol in solutions(opts=state.opts, **model):
        state.answer = sol.answer
        delta = sol.iter_time.end - last.iter_time.end
        if abs(delta.total_seconds() * 1000) >= debounce:
            last = sol
            await update(q, state)

    state.solving = False
    state.solve = None
    await update(q, state)


async def sync(q: Q, state: State):
    log_args(q)

    if q.args.day:
        state.day_num = q.args.day
    if q.args.part:
        state.part_num = q.args.part
    if q.args.engine:
        state.opts.engine = q.args.engine
    if q.args.processes:
        state.opts.processes = q.args.processes
    if q.args.timeout:
        state.opts.timeout = to_dur(seconds=q.args.timeout)
    if q.args.part_1:
        state.tab = Tab.part_1
    elif q.args.part_2:
        state.tab = Tab.part_2

    if q.args.solve and not state.solving:
        state.solving = True
        task = asyncio.ensure_future(solvex(q, state))
        state.solve = task
        return

    if q.args.solve and state.solving and state.solve:
        log.error(f"Cancelling solver")
        state.solving = False
        state.solve.cancel()
        state.solve = None
        return


async def update(q: Q, state: State):

    p = q.page["sidebar"]
    p.items[0].choice_group.value = state.day_num
    p.items[2].choice_group.value = state.part_num

    p = q.page["settings"]
    p.items[0].choice_group.value = state.part_num
    p.items[2].choice_group.value = state.opts.engine.name
    p.items[4].slider.value = int(state.opts.processes)
    p.items[6].slider.value = int(state.opts.timeout.total_seconds())
    p.items[8].button.label = "Cancel" if state.solving else "Solve"

    await q.page.save()


@app("/app")
async def serve(q: Q):

    await sync(q, state)
    await render(q, state)
    await update(q, state)