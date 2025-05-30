
def build_code_from_filter(spec):
    code = "filtered_df = df"
    filters = []

    if "month" in spec:
        filters.append(f"(df['Order Date'].dt.month == {spec['month']})")
    if "year" in spec:
        filters.append(f"(df['Order Date'].dt.year == {spec['year']})")
    if "country" in spec:
        filters.append(f"(df['Country'] == '{spec['country']}')")

    if filters:
        code = f"filtered_df = df[{ ' & '.join(filters) }]"

    return code
