def build_code_from_filter(spec):
    code = "filtered_df = df"
    filters = []

    if not spec:
        return code

    for key, value in spec.items():
        if key == "month":
            filters.append(f"(df['order date'].dt.month == {value})")
        elif key == "year":
            filters.append(f"(df['order date'].dt.year == {value})")
        elif key == "quarter":
            filters.append(f"(df['order date'].dt.quarter == {value})")
        elif key == "from_month":
            filters.append(f"(df['order date'].dt.month >= {value})")
        elif key == "to_month":
            filters.append(f"(df['order date'].dt.month <= {value})")
        elif key == "from_year":
            filters.append(f"(df['order date'].dt.year >= {value})")
        elif key == "to_year":
            filters.append(f"(df['order date'].dt.year <= {value})")

        # Exact match filters for all other lowercase columns
        elif key in [
            'row id', 'order id', 'ship date', 'ship mode', 'customer id', 'customer name',
            'segment', 'country', 'city', 'state', 'postal code', 'region', 'product id',
            'category', 'sub-category', 'product name'
        ]:
            filters.append(f"(df['{key}'] == '{value}')")

        else:
            print(f"Skipping unrecognized key: {key}")

    if filters:
        code = f"filtered_df = df[{' & '.join(filters)}]"

    return code
