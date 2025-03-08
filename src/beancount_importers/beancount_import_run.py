#!/usr/bin/env python3

import os
from pathlib import Path

import beancount_import.webserver
import click

from beancount_importers.importer_config import get_import_config, load_import_config_from_file


@click.command()
@click.option(
    "--journal_file",
    type=click.Path(),
    default="main.bean",
    help="Path to your main ledger file",
)
@click.option(
    "--importers_config_file",
    type=click.Path(),
    default=None,
    help="Path to the importers config file",
)
@click.option(
    "--data_dir",
    type=click.Path(),
    default="beancount_import_data",
    help="Directory with your import data (e.g. bank statements in csv)",
)
@click.option(
    "--output_dir",
    type=click.Path(),
    default="beancount_import_output",
    help="Where to put output files (don't forget to include them in your main ledger)",
)
@click.option(
    "--target_config",
    default="all",
    help="Note that specifying particular config will also result in transactions "
    + "being imported into specific output file for that config",
)
@click.option("--address", default="127.0.0.1", help="Web server address")
@click.option("--port", default="8101", help="Web server port")
def main(
    port,
    address,
    target_config,
    output_dir,
    data_dir,
    importers_config_file,
    journal_file,
):
    import_config = None
    if importers_config_file:
        import_config = load_import_config_from_file(
            importers_config_file, data_dir, output_dir
        )
    else:
        import_config = get_import_config(data_dir, output_dir)
    # Create output structure if it doesn't exist
    os.makedirs(
        os.path.dirname(import_config[target_config]["transactions_output"]),
        exist_ok=True,
    )
    Path(import_config[target_config]["transactions_output"]).touch()
    for file in [
        "accounts.bean",
        "balance_accounts.bean",
        "prices.bean",
        "ignored.bean",
    ]:
        Path(os.path.join(output_dir, file)).touch()

    beancount_import.webserver.main(
        {},
        port=port,
        address=address,
        journal_input=journal_file,
        ignored_journal=os.path.join(output_dir, "ignored.bean"),
        default_output=import_config[target_config]["transactions_output"],
        open_account_output_map=[
            (".*", os.path.join(output_dir, "accounts.bean")),
        ],
        balance_account_output_map=[
            (".*", os.path.join(output_dir, "balance_accounts.bean")),
        ],
        price_output=os.path.join(output_dir, "prices.bean"),
        data_sources=import_config[target_config]["data_sources"],
    )


if __name__ == "__main__":
    main()
