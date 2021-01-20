from h2o_wave import Q, main, app, ui
from src import *

days = {d.num: d for d in Day.s}


def title(day: Day):
    return f"Day {day.num} - {day.title}"


@app("/app")
async def serve(q: Q):
    day = days[q.args.day or 1]
    part = q.args.part or 1
    part = day.part_1 if part == 1 else day.part_2
    engine = Engine.parse(q.args.engine or Engine.GECODE)
    threads = 4
    timeout = 1

    if not q.client.init:
        q.client.init = True
        days_card = q.page.add(
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
                        value=day.num,
                    )
                ],
            ),
        )

        solver_card = q.page.add(
            "solver",
            ui.form_card(
                "8 1 2 8",
                items=[
                    ui.choice_group(
                        "engine",
                        label="Solver Engine",
                        choices=[ui.choice(name=e.name) for e in Engine],
                        value=engine.name,
                    ),
                    ui.separator(),
                    ui.slider(
                        "threads",
                        label="Max CPU Theads",
                        min=1,
                        max=48,
                        value=threads,
                        step=1,
                    ),
                    ui.separator(),
                    ui.slider(
                        "timeout",
                        label="Timeout (mins)",
                        min=1,
                        max=60,
                        value=timeout,
                        step=1,
                    ),
                ],
            ),
        )
        tab_card = q.page.add(
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

        form_card = q.page.add("form", ui.form_card(box="3 2 5 7", items=[]))

    q.page["sidebar"].items[0].choice_group.value = day.num
    q.page["sidebar"].items[2].choice_group.value = engine.name
    # q.page["tab"].items[0].text_xl.content = title(day)
    # q.page["tab"].items[1].choice_group.value = part.num

    await q.page.save()
