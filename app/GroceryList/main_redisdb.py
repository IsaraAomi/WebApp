from fastapi import FastAPI, HTTPException
from models import ItemPayload
import redis

app = FastAPI()

redis_client = redis.StrictRedis(host='0.0.0.0', port=6379, db=0, decode_responses=True)

# Route to add an item
@app.post("/items/{item_name}/{quantity}")
def add_item(item_name: str, quantity: int) -> dict[str, ItemPayload]:
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0.")
    # if item already exists, we'll just add the quantity.
    # get all item names
    item_id_str: str | None = redis_client.hget("item_name_to_id", item_name)

    if item_id_str is not None:
        # get index of item_name in item_ids, which is the item_id
        item_id = int(item_id_str)
        redis_client.hincrby(f"item_id:{item_id}", "quantity", quantity)
    # otherwise, create a new item
    else:
        # generate an ID for the item based on the highest ID in the grocery_list
        item_id: int = redis_client.incr("item_ids")
        redis_client.hset(
            f"item_id:{item_id}",
            mapping={
                "item_id": item_id,
                "item_name": item_name,
                "quantity": quantity,
            })
        redis_client.hset("item_name_to_id", item_name, item_id)

    item_quantity_str: str | None = redis_client.hget(f"item_id:{item_id}", "quantity")
    if item_quantity_str is None:
        item_quantity_int: int = 0
    else:
        item_quantity_int: int = int(item_quantity_str)

    return {"item": ItemPayload(item_id=item_id, item_name=item_name, quantity=item_quantity_int)}


# Route to list a specific item by ID
@app.get("/items/{item_id}")
def list_item(item_id: int) -> dict[str, dict[str, str]]:
    if not redis_client.hexists(f"item_id:{item_id}", "item_id"):
        raise HTTPException(status_code=404, detail="Item not found.")
    return {"item": redis_client.hgetall(f"item_id:{item_id}")}


# Route to list all items
@app.get("/items")
def list_items() -> dict[str, list[ItemPayload]]:
    items:list[ItemPayload] = []
    stored_items: dict[str, str] = redis_client.hgetall("item_name_to_id")

    for name, id_str in stored_items.items():
        item_id = int(id_str)
        item_name_str: str | None = redis_client.hget(f"item_id:{item_id}", "item_name")
        if item_name_str is not None:
            item_name: str = item_name_str
        else:
            continue

        item_quantity_str: str | None = redis_client.hget(f"item_id:{item_id}", "quantity")
        if item_quantity_str is not None:
            item_quantity = int(item_quantity_str)
        else:
            item_quantity = 0

        items.append(ItemPayload(item_id=item_id, item_name=item_name, quantity=item_quantity))

    return {"items": items}


# Route to delete a specific item by ID
@app.delete("/items/{item_id}")
def delete_item(item_id: int) -> dict[str, str]:
    if not redis_client.hexists(f"item_id:{item_id}", "item_id"):
        raise HTTPException(status_code=404, detail="Item not found.")
    else:
        item_name: str | None = redis_client.hget(f"item_id:{item_id}", "item_name")
        redis_client.hdel("item_name_to_id", f"{item_name}")
        redis_client.delete(f"item_id:{item_id}")
        return {"result": f"Item({item_name}) deleted."}


# Route to remove some quantity of a specific item by ID
@app.delete("/items/{item_id}/{quantity}")
def remove_quantity(item_id: int, quantity: int) -> dict[str, str]:
    if not redis_client.hexists(f"item_id:{item_id}", "item_id"):
        raise HTTPException(status_code=404, detail="Item not found.")
    
    item_name: str | None = redis_client.hget(f"item_id:{item_id}", "item_name")
    item_quantity: str | None = redis_client.hget(f"item_id:{item_id}", "quantity")

    # if quantity to be removed is higher or equal to item's quantity, delete the item
    if item_quantity is None:
        existing_quantity: int = 0
    else:
        existing_quantity: int = int(item_quantity)
    if  existing_quantity <= quantity:
        redis_client.hdel("item_name_to_id", f"{item_name}")
        redis_client.delete(f"item_id:{item_id}")
        return {"result": f"Item({item_name}) deleted."}
    else:
        pre_quantity: int = existing_quantity
        post_quantity: int = pre_quantity - quantity
        redis_client.hincrby(f"item_id:{item_id}", "quantity", -quantity)
    return {
        "result": f"Item({item_name}) {quantity} removed: {pre_quantity} -> {post_quantity}"
    }
