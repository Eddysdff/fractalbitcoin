import mnemonic
import pandas as pd
from bip_utils import Bip39SeedGenerator, Bip84, Bip84Coins, Bip44Changes

def generate_btc_wallet(num_wallets):
    wallets = []
    for _ in range(num_wallets):
        # 生成助记词
        m = mnemonic.Mnemonic("english")
        mnemonic_words = m.generate(strength=256)  # 24个单词的助记词

        # 从助记词生成种子
        seed = Bip39SeedGenerator(mnemonic_words).Generate()

        # 使用BIP84生成SegWit地址
        bip84_mst_ctx = Bip84.FromSeed(seed, Bip84Coins.BITCOIN)
        bip84_acc_ctx = bip84_mst_ctx.Purpose().Coin().Account(0)
        bip84_chg_ctx = bip84_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
        bip84_addr_ctx = bip84_chg_ctx.AddressIndex(0)

        address = bip84_addr_ctx.PublicKey().ToAddress()
        private_key = bip84_addr_ctx.PrivateKey().Raw().ToHex()

        wallets.append({
            'address': address,
            'private_key': private_key,
            'mnemonic': mnemonic_words
        })

    return wallets

def save_to_excel(wallets, filename):
    df = pd.DataFrame(wallets)
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"已将钱包信息保存到 {filename}")

if __name__ == "__main__":
    num_wallets = int(input("请输入要生成的钱包数量："))
    wallets = generate_btc_wallet(num_wallets)
    save_to_excel(wallets, "fractalwallet_daaress.xlsx")