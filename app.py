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
    problem = auto()
    model = auto()
    data = auto()


@attr.s
class App(Base):

    # fmt:off
    init    : bool      = attr.ib(default=False)
    day_num : int       = attr.ib(default=1)
    part_num: int       = attr.ib(default=1)
    opts    : SolveOpts = attr.ib(factory = SolveOpts)
    tab     : Tab       = attr.ib(default=Tab.problem, converter=Tab.parse) # type:ignore
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

    @property
    def part_1(self):
        return self.day.part_1

    @property
    def part_2(self):
        return self.day.part_2


def log_args(q: Q):
    for k, v in q.args.__dict__["__kv"].items():
        log.debug(f"arg {k}:{type(v).__name__} = {v}")


def log_app(app: App):
    for k, v in app.__dict__.items():
        log.info(f"app {k}:{type(v).__name__} = {v}")


state = App()

rows = 12
cols = 12


def box(x0=1, y0=1, dx=cols, dy=rows, x1=None, y1=None):
    if x1 is not None:
        dx = x1 - x0
    if y1 is not None:
        dy = y1 - y0
    return f"{x0} {y0} {dx} {dy}"


async def render(q: Q, app: App):
    if app.init:
        return

    app.init = True

    q.page.add("meta", ui.meta_card(box="", title=""))

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

    app.settings = q.page.add(
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
            box(3, 2, 5),
            items=[
                ui.tabs(
                    "tab",
                    items=[
                        ui.tab("problem", "Problem", icon="Info"),
                        ui.tab("model", "Model", icon="Code"),
                        ui.tab("data", "Data", icon="Database"),
                    ],
                    value="problem",
                ),
                ui.text_m(""),
            ],
        ),
    )
    q.page.add("viz", ui.vega_card(box=box(8, 2, 5), title="Viz", specification=c))
    await q.page.save()


async def solvex(q: Q, state: App, debounce=100):

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


async def sync(q: Q, app: App):
    """
    Sync the application state with the client
    """

    log_args(q)

    if q.args.day:
        app.day_num = q.args.day
    if q.args.part:
        app.part_num = q.args.part
    if q.args.engine:
        app.opts.engine = q.args.engine
    if q.args.processes:
        app.opts.processes = q.args.processes
    if q.args.timeout:
        app.opts.timeout = to_dur(seconds=q.args.timeout)
    if q.args.tab:
        app.tab = q.args.tab

    app.part_num = 1 if q.args.part == 1 else 2

    if "#" in q.args:
        x = str(q.args["#"])
        if x.isnumeric():
            app.day_num = int(x)

    if q.args.solve and not app.solving:
        app.solving = True
        task = asyncio.ensure_future(solvex(q, app))
        app.solve = task
        return

    if q.args.solve and app.solving and app.solve:
        log.error(f"Cancelling solver")
        app.solving = False
        app.solve.cancel()
        app.solve = None
        return


async def update(q: Q, app: App):

    q.page["meta"].theme = "light"
    p = q.page["settings"]

    p.items[0].choice_group.label = title(app.day)
    p.items[0].choice_group.value = app.part_num
    p.items[0].choice_group.disabled = app.solving

    p.items[2].dropdown.value = app.opts.engine.name
    p.items[2].dropdown.disabled = app.solving

    p.items[4].slider.value = int(app.opts.processes)
    p.items[4].slider.disabled = app.solving

    p.items[6].slider.value = int(app.opts.timeout.total_seconds())
    p.items[6].slider.disabled = app.solving

    p.items[8].button.label = "Cancel" if app.solving else "Solve"

    p = q.page["header"]
    p.title = f"Advent of Code 2020 - Day {app.day.num} - {app.day.title}"

    p = q.page["main"]
    p.items[0].tabs.value = app.tab.name

    if app.tab == Tab.problem:
        wrapper = textwrap.TextWrapper(
            width=80, break_long_words=False, replace_whitespace=False
        )
        txt = f"## Part 1\n\n" + app.part_1.blurb
        if app.part_num == 2:
            txt += f"\n\n## Part 2\n\n{app.part_2.blurb}"

        text = textwrap.dedent(txt)
        text = "\n".join(wrapper.wrap(text))

    elif app.tab == Tab.model:
        data = app.day.data
        model, params = app.part.formulate(data)
        text = model

    else:
        data = app.day.data
        text = json.dumps(cattr.unstructure(data), indent=4).replace("\n", "\n\n")

    p.items[1].text_m.content = text

    await q.page.save()


@app("/app")
async def serve(q: Q):
    await sync(q, state)
    await render(q, state)
    await update(q, state)