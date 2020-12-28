from h2o_wave import Q, main, app, ui
from src import *

names = [p.name for p in Problem.list]


@app("/app")
async def serve(q: Q):
    name = q.args.problem or ""

    if not q.client.init:
        q.client.init = True
        q.page["form"] = ui.form_card(
            box="1 1 3 10",
            items=[
                ui.choice_group(
                    "problem",
                    choices=[ui.choice(name=n, label=n) for n in names],
                    trigger=True,
                    value=name,
                ),
                ui.label(name),
            ],
        )
    else:
        q.page["form"].items[0].choice_group.value = name
        q.page["form"].items[1].label.label = name

    await q.page.save()
