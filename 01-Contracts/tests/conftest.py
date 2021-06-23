import pytest
from brownie import (
    config,
    network,
    accounts,
    Token,
    StreamUnlockableNFTFactory,
    SimpleNFT,
)
from brownie import Token



@pytest.fixture
def queen(accounts):
    """Creator of the SUNFT, owner of some NFTs"""
    return accounts[0]

@pytest.fixture
def creator(accounts):
    """Creator of the SUNFT, owner of some NFTs"""
    return accounts[1]

@pytest.fixture
def owner(accounts):
    """Owner of the SUNFT"""
    return accounts[2]

@pytest.fixture
def dai(owner, Token):
    return owner.deploy(Token, "DAI", "DAI", 18, 1000 * 10**18)

@pytest.fixture
def gambit(queen, dai):
    """An NFT contract with a few NFTs minted to creator"""
    _nft = queen.deploy(StreamUnlockableNFTFactory, dai.address, 1e18)
    return _nft

@pytest.fixture
def nft(SimpleNFT, queen, creator, owner):
    """An NFT contract with a few NFTs minted to creator"""
    _nft = queen.deploy(SimpleNFT)
    _nft.createCollectible("ipfs://0000", {"from": creator})
    _nft.createCollectible("ipfs://1111", {"from": creator})
    return _nft

@pytest.fixture
def seven_days():
    return 60 * 60 * 24 * 7 + 60    # plus 1 min.

@pytest.fixture
def thirty_days():
    return 60 * 60 * 24 * 7 + 60    # plus 1 min.

@pytest.fixture
def stream_rate():
    return 1000

@pytest.fixture
def minting_fee():
    return 1e18

@pytest.fixture
def sunft(nft, gambit, queen, creator, owner, seven_days, stream_rate,minting_fee):
    # Approve 2 NFTs to lock into a SUNFT
    nft.approve(gambit.address, 0, {"from": creator})
    nft.approve(gambit.address, 1, {"from": creator})

    # Mint the SUNFT directly to its owner, append the 2nd NFT after mint
    bal = creator.balance()

    _sunft_id = gambit.mint(nft.address, 0, stream_rate, seven_days, owner, {"from": creator, "value": 10**18}).return_value
    gambit.append(nft.address, 1, stream_rate, seven_days, 1, {"from": creator})

    after_mint_bal = creator.balance()

    assert bal - after_mint_bal == minting_fee

    return _sunft_id
