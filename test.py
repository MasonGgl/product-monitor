from api import calculate_price_change

print(calculate_price_change([]))
print(calculate_price_change([{'price':50}]))
print(calculate_price_change([{'price':60},{'price':50}]))
print(calculate_price_change([{'price':40},{'price':50}]))