import matplotlib
from graphmaker.resources import VTDShapefile
from graphmaker.geospatial import reprojected

matplotlib.use('Agg')

import matplotlib.pyplot as plt  # noqa: E402


def chloropleth(fips, column, filepath='./output.png'):
    df = VTDShapefile(fips).as_df()
    df = reprojected(df)

    if isinstance(column, str):
        column_name = column
    else:
        column_name = 'column'
        df['column'] = column

    _, ax = plt.subplots(1)
    df.plot(ax=ax, linewidth=0.5, edgecolor='0.5', column=column_name)
    ax.set_axis_off()

    plt.axis('equal')
    plt.savefig(filepath)
