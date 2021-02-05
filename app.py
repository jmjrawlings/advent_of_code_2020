from enum import auto
from os import sep
from h2o_wave import Q, main, app, ui
from src import *
import altair as alt
import textwrap
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

rows = 12
cols = 12


def box(x0=1, y0=1, dx=cols, dy=rows, x1=None, y1=None):
    if x1 is not None:
        dx = x1 - x0
    if y1 is not None:
        dy = y1 - y0
    return f"{x0} {y0} {dx} {dy}"


async def render(q: Q, app: State):
    if app.init:
        return

    app.init = True

    q.page.add("meta", ui.meta_card(box="", title="Advent of Code 2020"))

    q.page.add(
        "header",
        ui.header_card(
            # Place card in the header zone, regardless of viewport size.
            box=box(dy=1),
            title="Advent of Code 2020",
            subtitle="",
            nav=[
                ui.nav_group(
                    "Problems",
                    collapsed=False,
                    items=[
                        ui.nav_item(f"#{d.num}", f"{d.num} - {d.title}") for d in Day.s
                    ],
                )
            ],
        ),
    )

    q.page.add(
        "settings",
        ui.form_card(
            box=box(1, 2, 2),
            items=[
                ui.choice_group(
                    "part",
                    label=title(app.day),
                    choices=[
                        ui.choice(1, "Part 1"),
                        ui.choice(2, "Part 2"),
                    ],
                    trigger=True,
                    value=app.day_num,
                ),
                ui.separator(),
                ui.dropdown(
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
                    max=12,
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
    q.page.add(
        "main",
        ui.form_card(
            box(3, 2, 6),
            items=[
                ui.tabs(
                    "tabs",
                    items=[
                        ui.tab("problem", "Problem", icon="Info"),
                        ui.tab("model", "Model", icon="Code"),
                        ui.tab("data", "Data", icon="Database"),
                    ],
                ),
            ],
        ),
    )
    q.page.add("form", ui.vega_card(box=box(8, 2, 5), title="Viz", specification=c))
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

    state.part_num = 1 if q.args.part == 1 else 2

    if "#" in q.args:
        x = str(q.args["#"])
        if x.isnumeric():
            state.day_num = int(x)

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

    # p.items[0].choice_group.value = state.day_num
    # p.items[2].choice_group.value = state.part_num

    p = q.page["settings"]
    p.items[0].choice_group.label = title(state.day)
    p.items[0].choice_group.value = state.part_num
    p.items[0].choice_group.disabled = state.solving

    p.items[2].dropdown.value = state.opts.engine.name
    p.items[2].dropdown.disabled = state.solving

    p.items[4].slider.value = int(state.opts.processes)
    p.items[4].slider.disabled = state.solving

    p.items[6].slider.value = int(state.opts.timeout.total_seconds())
    p.items[6].slider.disabled = state.solving

    p.items[8].button.label = "Cancel" if state.solving else "Solve"

    p = q.page["model"]
    wrapper = textwrap.TextWrapper(
        width=70, break_long_words=False, replace_whitespace=False
    )
    if state.part_num == 1:
        text = state.part.blurb
    else:
        text = state.day.part_1.blurb + "\n\n" + state.day.part_2.blurb

    text = textwrap.dedent(text)
    text = "\n".join(wrapper.wrap(text))
    p.content = text
    p.title = state.part.title
    # "\r".join(textwrap.wrap(state.part.blurb, width=80)).replace("\t", " ")
    # p.title = state.part.title

    await q.page.save()


@app("/app")
async def serve(q: Q):

    await sync(q, state)
    await render(q, state)
    await update(q, state)