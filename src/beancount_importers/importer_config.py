import os

import yaml
from uabean.importers import binance, ibkr, kraken, monobank

import beancount_importers.import_monzo as import_monzo
import beancount_importers.import_revolut as import_revolut
import beancount_importers.import_wise as import_wise


def get_importer_config(type, account, currency, importer_params):
    common = dict(type=type, account=account, currency=currency)
    if type == "monzo":
        return dict(
            **common,
            module="beancount_import.source.generic_importer_source_beangulp",
            importer=import_monzo.get_importer(account, currency, importer_params),
            description=(
                "In the app go to Help > Download a statement. "
                "The easiest way would be just to download monthly statements every month."
            ),
            emoji="💷"
        )
    elif type == "wise":
        return dict(
            **common,
            module="beancount_import.source.generic_importer_source_beangulp",
            importer=import_wise.get_importer(account, currency),
            description="Can be downloaded online from https://wise.com/balances/statements",
            emoji="💵"
        )
    elif type == "revolut":
        return dict(
            **common,
            module="beancount_import.source.generic_importer_source_beangulp",
            importer=import_revolut.get_importer(account, currency),
            emoji="💵"
        )
    elif type == "ibkr":
        return dict(
            **common,
            module="beancount_import.source.generic_importer_source_beangulp",
            importer=ibkr.Importer(
                use_existing_holdings=False, **(importer_params or {})
            ),
            description=(
                "Go to Performance & Reports > Flex Queries. "
                'Create new one. Enable "Interest accruals", "Cash Transactions", "Trades", "Transfers". '
                'From "Cash Transactions" disable fields "FIGI", "Issuer Country Code", "Available For Trading Date". '
                'From "Trades" disable "Sub Category", "FIGI", "Issuer Country Code", "Related Trade ID", '
                '"Orig *", "Related Transaction ID", "RTN", "Initial Investment". Otherwise importer may break.'
            ),
            emoji="📈"
        )
    elif type == "monobank":
        mapped_account_config = {}
        for p in importer_params.get("account_config", []):
            tp = p[0]
            currency = p[1]
            account = p[2]
            mapped_account_config[(tp, currency)] = account
        mapped_params = importer_params.copy()
        mapped_params["account_config"] = mapped_account_config
        return dict(
            **common,
            module="beancount_import.source.generic_importer_source_beangulp",
            importer=monobank.Importer(**mapped_params),
            emoji="💵"
        )
    elif type == "kraken":
        return dict(
            **common,
            module="beancount_import.source.generic_importer_source_beangulp",
            importer=kraken.Importer(**(importer_params or {})),
            emoji="🎰"
        )
    elif type == "binance":
        return dict(
            **common,
            module="beancount_import.source.generic_importer_source_beangulp",
            importer=binance.Importer(**(importer_params or {})),
            emoji="🎰"
        )
    else:
        return None


def load_import_config_from_file(filename, data_dir, output_dir):
    with open(filename, "r") as config_file:
        parsed_config = yaml.safe_load(config_file)
        data_sources = []
        for key, params in parsed_config["importers"].items():
            config = dict(
                directory=os.path.join(data_dir, key),
                **get_importer_config(
                    params["importer"],
                    params.get("account"),
                    params.get("currency"),
                    params.get("params"),
                )
            )
            data_sources.append(config)
        return dict(
            all=dict(
                data_sources=data_sources,
                transactions_output=os.path.join(output_dir, "transactions.bean"),
            )
        )


def get_import_config(data_dir, output_dir):
    import_config = {
        "monzo": dict(
            data_sources=[
                dict(
                    module="beancount_import.source.generic_importer_source_beangulp",
                    importer=import_monzo.get_importer("Assets:Monzo:Cash", "GBP"),
                    account="Assets:Monzo:Cash",
                    directory=os.path.join(data_dir, "monzo"),
                )
            ],
            transactions_output=os.path.join(output_dir, "monzo", "transactions.bean"),
        ),
        "wise_usd": dict(
            data_sources=[
                dict(
                    module="beancount_import.source.generic_importer_source_beangulp",
                    importer=import_wise.get_importer("Assets:Wise:Cash", "USD"),
                    account="Assets:Wise:Cash",
                    directory=os.path.join(data_dir, "wise_usd"),
                )
            ],
            transactions_output=os.path.join(
                output_dir, "wise_usd", "transactions.bean"
            ),
        ),
        "wise_gbp": dict(
            data_sources=[
                dict(
                    module="beancount_import.source.generic_importer_source_beangulp",
                    importer=import_wise.get_importer("Assets:Wise:Cash", "GBP"),
                    account="Assets:Wise:Cash",
                    directory=os.path.join(data_dir, "wise_gbp"),
                )
            ],
            transactions_output=os.path.join(
                output_dir, "wise_gbp", "transactions.bean"
            ),
        ),
        "wise_eur": dict(
            data_sources=[
                dict(
                    module="beancount_import.source.generic_importer_source_beangulp",
                    importer=import_wise.get_importer("Assets:Wise:Cash", "EUR"),
                    account="Assets:Wise:Cash",
                    directory=os.path.join(data_dir, "wise_eur"),
                )
            ],
            transactions_output=os.path.join(
                output_dir, "wise_eur", "transactions.bean"
            ),
        ),
        "revolut_usd": dict(
            data_sources=[
                dict(
                    module="beancount_import.source.generic_importer_source_beangulp",
                    importer=import_revolut.get_importer("Assets:Revolut:Cash", "USD"),
                    account="Assets:Revolut:Cash",
                    directory=os.path.join(data_dir, "revolut_usd"),
                )
            ],
            transactions_output=os.path.join(
                output_dir, "revolut", "transactions.bean"
            ),
        ),
        "revolut_gbp": dict(
            data_sources=[
                dict(
                    module="beancount_import.source.generic_importer_source_beangulp",
                    importer=import_revolut.get_importer("Assets:Revolut:Cash", "GBP"),
                    account="Assets:Revolut:Cash",
                    directory=os.path.join(data_dir, "revolut_gbp"),
                )
            ],
            transactions_output=os.path.join(
                output_dir, "revolut", "transactions.bean"
            ),
        ),
        "revolut_eur": dict(
            data_sources=[
                dict(
                    module="beancount_import.source.generic_importer_source_beangulp",
                    importer=import_revolut.get_importer("Assets:Revolut:Cash", "EUR"),
                    account="Assets:Revolut:Cash",
                    directory=os.path.join(data_dir, "revolut_eur"),
                )
            ],
            transactions_output=os.path.join(
                output_dir, "revolut", "transactions.bean"
            ),
        ),
        "ibkr": dict(
            data_sources=[
                dict(
                    module="beancount_import.source.generic_importer_source_beangulp",
                    importer=ibkr.Importer(),
                    account="Assets:IB",
                    directory=os.path.join(data_dir, "ibkr"),
                )
            ],
            transactions_output=os.path.join(output_dir, "ibkr", "transactions.bean"),
        ),
    }
    import_config_all = dict(
        data_sources=[],
        transactions_output=os.path.join(output_dir, "transactions.bean"),
    )
    for k, v in import_config.items():
        import_config_all["data_sources"].extend(v["data_sources"])

    import_config["all"] = import_config_all
    return import_config
