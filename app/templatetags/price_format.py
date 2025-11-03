from django import template

register = template.Library()

@register.filter(name='indian_currency')
def indian_currency(value):
    try:
        value = int(value)
        s = f"{value:,}"  # e.g., 1,234,567
        # Convert to Indian format (##,##,###)
        x = str(value)[::-1]
        lst = []
        lst.append(x[:3])
        for i in range(3, len(x), 2):
            lst.append(x[i:i+2])
        formatted = ','.join(lst)[: : -1]
        return f"{formatted}"
    except:
        return value
