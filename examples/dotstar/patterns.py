"""Advanced pattern examples."""

from dotstar import search, find_all, Pattern

# E-commerce data
store_data = {
    "categories": {
        "electronics": {
            "products": [
                {
                    "id": 101,
                    "name": "Laptop",
                    "price": 999,
                    "inventory": {"warehouse": 50, "store": 5}
                },
                {
                    "id": 102,
                    "name": "Mouse",
                    "price": 29,
                    "inventory": {"warehouse": 200, "store": 25}
                }
            ]
        },
        "books": {
            "products": [
                {
                    "id": 201,
                    "name": "Python Guide",
                    "price": 39,
                    "inventory": {"warehouse": 100, "store": 10}
                }
            ]
        }
    }
}

print("=== Inventory Analysis ===")

# Get all warehouse quantities
warehouse = search(store_data, "categories.*.products.*.inventory.warehouse")
print(f"Total warehouse items: {sum(warehouse)}")

# Get all store quantities
store = search(store_data, "categories.*.products.*.inventory.store")
print(f"Total store items: {sum(store)}")

# Find products low on store inventory
print("\nLow inventory items:")
products = find_all(store_data, "categories.*.products.*")
for path, product in products:
    if isinstance(product, dict) and product.get('inventory', {}).get('store', 0) < 10:
        print(f"  - {product['name']}: only {product['inventory']['store']} in store")

print("\n=== Price Analysis ===")

# Get all prices
prices = search(store_data, "categories.*.products.*.price")
print(f"Price range: ${min(prices)} - ${max(prices)}")
print(f"Average price: ${sum(prices) / len(prices):.2f}")

print("\n=== Pattern Composition ===")

# Build patterns incrementally
PRODUCTS = Pattern("categories.*.products.*")
PRICES = PRODUCTS / "price"
INVENTORY = PRODUCTS / "inventory"
WAREHOUSE_STOCK = INVENTORY / "warehouse"

print(f"All prices: {PRICES.search(store_data)}")
print(f"Warehouse stock: {WAREHOUSE_STOCK.search(store_data)}")
