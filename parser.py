import argparse


def prepare_parser():
    parser = argparse.ArgumentParser(
        description="Generate PDFs for GCP ACE exam questions"
    )
    parser.add_argument(
        "--start", default=120, type=int, help="First question index to query"
    )
    parser.add_argument(
        "--end", default=190, type=int, help="Last question index to query"
    )
    parser.add_argument(
        "--pages", default=[3, 5], type=int, nargs="+", help="Specify pages to generate"
    )
    return parser
