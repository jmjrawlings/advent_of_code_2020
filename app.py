from h2o_wave import Q, main, app, ui
from src import *

days = list(Problem.by_day.keys())


@app("/app")
async def serve(q: Q):
    day = q.args.day or 1
    part = q.args.part or 1
    engine = Engine.parse(q.args.engine or Engine.GECODE)
    threads = 4
    timeout = 1
    problem = Problem.map[day, part]
    log.info(days)
    log.info(
        f"{q.client.init} D{day} {type(day)} P{part}{type(part)} E{engine} {problem.name}"
    )

    if not q.client.init:
        q.client.init = True
        q.page["sidebar"] = ui.form_card(
            box="1 1 2 8",
            items=[
                ui.dropdown(
                    "day",
                    label="Day",
                    choices=[ui.choice(t) for t in days],
                    trigger=True,
                    value=day,
                ),
                ui.choice_group(
                    "part",
                    label="Part",
                    choices=[ui.choice(1), ui.choice(2)],
                    trigger=True,
                    value=part,
                ),
                ui.separator(),
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
        )
        q.page["main"] = ui.form_card(
            box="3 1 6 8",
            items=[
                ui.text_xl(problem.title),
            ],
        )
    else:
        q.page["sidebar"].items[0].dropdown.value = day
        q.page["sidebar"].items[1].choice_group.value = part
        q.page["sidebar"].items[3].choice_group.value = engine.name
        q.page["main"].items[0].text_xl.content = problem.title

    await q.page.save()
