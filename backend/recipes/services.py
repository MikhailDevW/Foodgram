from django.http import HttpResponse
from reportlab.pdfgen import canvas

LINE_OFFSET = 20
X_COORDINATE = 100
INITIAL_Y_COORDINATE = 750


def get_report(ingrediend_list: list) -> HttpResponse:
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_cart.pdf"'
    )
    file = canvas.Canvas(response)
    file.drawString(100, 800, ('Shopping list'))
    y_coord = INITIAL_Y_COORDINATE
    for component in ingrediend_list:
        name = component.get(
            'ingredient__name',
            'Не определено')
        amount = component.get(
            'amount',
            'Не определено')
        m_unit = component.get(
            'ingredient__measurement_unit',
            'Не определено')
        file.drawString(
            X_COORDINATE,
            y_coord,
            f'{name} - {amount} - {m_unit}'
        )
        y_coord -= LINE_OFFSET
    file.showPage()
    file.save()
    return response
