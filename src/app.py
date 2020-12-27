from .prelude import *
from h2o_wave import Q, main, app, ui
from src import day_1

problems = [day_1.Part1, day_1.Part2]


@app("/app")
async def serve(q: Q):

    problem = problems[q.client.index or 0]

    def render(q: Q):

        q.page["form"] = ui.form_card(
            box="1 1 3 10",
            items=[],
        )

    await q.page.save()
