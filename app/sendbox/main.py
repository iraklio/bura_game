from fastapi import FastAPI, HTTPException

from starknet_py.contract import Contract
from starknet_py.net.client import Client

API_VERSION = "0.0.1"
app = FastAPI()
starknet_client = Client("testnet")


contract_address = "0x029af160331cb2c5898999034f51f3357243a36b93c7b696f7daf0711482458e"
vehicle_id = 3
private_key = 12345
public_key = (
    1628448741648245036800002906075225705100596136133912895015035902954123957052
)


@app.get(path="/api")
async def api_info():
    return {"version": API_VERSION}


@app.get(path="/api/tmp")
async def tmp_block():
    """A temporary function to demonstrate network interaction"""
    # Replace this with the block hash of your deployment from Part 1
    call_result = await starknet_client.get_block(
        "0xf93145481a5ec656966de0ff6bfe507a2dec4fcbdb07a37cb8a2d3292305fb"
    )
    return call_result


@app.get(path="/api/register")
async def register():
    """Registers the car on chain, using configured data"""
    contract = await Contract.from_address(contract_address, starknet_client)

    # Calling a contract's function doesn't create a new transaction,
    # you get the function's result immediately. Use `call` for @views
    (owner,) = await contract.functions["get_owner"].call(vehicle_id)
    if owner != 0:
        raise HTTPException(status_code=403, detail="Vehicle already registered")

    # Writes (i.e. invokes) aren't accepted immediately.
    # Use `invoke` for @externals
    invocation = await contract.functions["register_vehicle"].invoke(
        vehicle_id=vehicle_id,
        owner_public_key=public_key,
        signer_public_key=public_key,
        max_fee=100000000,
    )

    # ... but we can easily wait for it
    await invocation.wait_for_acceptance()

    return {"tx_hash": invocation.hash}
