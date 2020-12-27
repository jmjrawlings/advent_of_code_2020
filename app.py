from h2o_wave import Q, main, app, ui
from src import *

names = [p.name for p in Problem.list]


@app("/app")
async def serve(q: Q):
    name = q.client.problem or ""
    log.error(name)

    form = q.page.add(
        "form",
        ui.form_card(
            box="1 1 3 10",
            items=[
                ui.choice_group(
                    "problem",
                    trigger=True,
                    choices=[ui.choice(name=n, label=n) for n in names],
                ),
            ],
        ),
    )

    await q.page.save()
