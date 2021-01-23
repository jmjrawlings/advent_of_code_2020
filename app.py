from datetime import time
from h2o_wave import Q, main, app, ui
from src import *

days = {d.num: d for d in Day.s}


def title(day: Day):
    return f"Day {day.num} - {day.title}"


@attr.s
class App:
    day_num: int = attr.ib(default=1)
    part_num: int = attr.ib(default=1)
    engine: Engine = attr.ib(default=Engine.CHUFFED, converter=Engine.parse)
    threads: int = attr.ib(default=4)
    timeout: Duration = attr.ib(default=to_dur(seconds=10), converter=to_dur)

    @property
    def day(self):
        return days[self.day_num]

    @property
    def part(self):
        if self.part_num == 1:
            return self.day.part_1
        else:
            return self.day.part_2


async def setup(q: Q, app: App):
    q.client.init = True
    q.page.add(
        "days",
        ui.form_card(
            box="1 1 2 8",
            items=[
                ui.choice_group(
                    "day",
                    label="Advent of Code 2020",
                    choices=[
                        ui.choice(name=d.num, label=title(d)) for d in days.values()
                    ],
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
                    label="Timeout (mins)",
                    min=1,
                    max=60,
                    value=int(app.timeout.total_minutes()),
                    step=1,
                ),
            ],
        ),
    )

    q.page.add(
        "tab",
        ui.tab_card(
            box="3 1 5 1",
            items=[
                ui.tab("input", "Input Data"),
                ui.tab("part_1", "Part 1"),
                ui.tab("part_2", "Part 2"),
            ],
        ),
    )

    q.page.add("form", ui.form_card(box="3 2 5 7", items=[]))


@app("/app")
async def serve(q: Q):

    app = App(
        day_num=q.args.day or 1,
        part_num=q.args.part or 1,
        engine=q.args.engine or Engine.GECODE,
        threads=4,
        timeout=to_dur(seconds=10),
    )

    print(app)

    if not q.client.init:
        await setup(q, app)

    q.page["sidebar"].items[0].choice_group.value = app.day_num
    q.page["sidebar"].items[2].choice_group.value = app.part_num
    # q.page["tab"].items[0].text_xl.content = title(day)
    # q.page["tab"].items[1].choice_group.value = part.num

    await q.page.save()
