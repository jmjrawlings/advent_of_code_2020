from typing import List
from h2o_wave import Q, main, app, ui


async def serve(q: Q):
    render(q)
    await q.page.save()


@app("/app")
async def serve(q: Q):
    render(q)
    await q.page.save()


def render(q: Q):

    q.page["form"] = ui.form_card(
        box="1 1 3 10",
        items=[],
    )
