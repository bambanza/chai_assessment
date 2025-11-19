from .ingest import run_ingest
from .transform import run_transform
from .model import run_model


def main():
    print("=== CHAI Weather ETL – Pipeline Start ===")
    run_ingest()
    run_transform()
    run_model()
    print("=== CHAI Weather ETL – Pipeline Done ===")


if __name__ == "__main__":
    main()
