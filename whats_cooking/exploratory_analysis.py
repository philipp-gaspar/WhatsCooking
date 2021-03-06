from __future__ import division

import sys
import os
from math import pi

import numpy as np
import pandas as pd

from collections import Counter
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='darkgrid', font_scale=1.5)

# =========
# FUNCTIONS
# =========
def create_folder(complete_path):
    """
    Function to create a folder.

    Parameter
    ---------
    complete_path : str
        Complete path of the new folder.

    Returns
    -------
    Create the new folder.
    """
    if not os.path.exists(complete_path):
        os.makedirs(complete_path)

    return 0

def clean_cuisine_names(cuisine_names):
    """
    String manipulation of cuisine names.

    Parameter:
    ---------
    cuisine_names : list
        List containg the cuisine names.

    Returns:
    -------
    clean_names : list
        List with the with the new names.
    """
    clean_names = []

    for i, name in enumerate(cuisine_names):
        new_name = name.title()

        if new_name.find('_') > 0:
            new_name = new_name.replace('_', ' ')

        clean_names.append(new_name)

    return clean_names

def parallel_counting(data):
    """
    Auxiliary function for parallel counting.
    """
    return data.map(Counter).sum()

def ingredients_counter(data):
    """
    Function to count the ingredients in parallel fashion.

    Parameter:
    ---------
    data : pandas series
        Pandas Series object with the ingredients for counting.

    Returns:
    -------
    ingredients_count : pandas series
        Series with count for each ingredient.

    Note:
    ----
    The ingredients are returned in descending order
    """
    # Let's make this counter process parallel
    # using the 'multiprocessing' library
    cores = cpu_count()

    # separate data into chunks for the parallel processing
    data_chunks = np.array_split(data, cores)

    pool = Pool(cores)
    counter_list = pool.map(parallel_counting, data_chunks)
    pool.close()

    ingredients_count = pd.Series(sum(counter_list, \
    Counter())).sort_values(ascending=False)

    return ingredients_count

if __name__ == '__main__':

    # =======
    # FOLDERS
    # =======
    package_path = os.path.dirname(os.getcwd())
    data_path = os.path.join(package_path, 'data')

    # create folder for figures
    fig_path = os.path.join(package_path, 'figures')
    create_folder(fig_path)

    # =========
    # LOAD DATA
    # =========
    input_file = os.path.join(data_path, 'train.json')

    df = pd.read_json(input_file)

    # get the total number of recipes
    n_recipes = df.shape[0]
    print('>> Data <<')
    print('    The training dataset has %i recipes.\n' % (n_recipes))

    # ========
    # CUISINES
    # ========
    cuisine = df['cuisine'].value_counts()
    n_cuisines = cuisine.nunique()
    print('>> Cuisines <<')
    print('    This dataset has %i different cuisines.' % n_cuisines)

    cuisine_names = list(cuisine.index)
    cuisine_values = list(cuisine.values)
    cuisine_clean_names = clean_cuisine_names(cuisine_names)


    # cuisines bar plot
    fig_file = os.path.join(fig_path, 'cuisines_barplot.pdf')

    plt.figure(figsize=(10, 7))
    sns.barplot(x=cuisine_values,
                y=cuisine_clean_names,
                edgecolor=(0, 0, 0),
                linewidth=1)
    plt.xlabel('Counts')
    plt.ylabel('Cuisines')
    plt.savefig(fig_file, bbox_inches='tight', dpi=1200)
    plt.close()

    # cuisines pie chart
    fig_file = os.path.join(fig_path, 'cuisines_piechart.pdf')
    top_cuisines = 5
    short_cuisine_values = cuisine_values[0:top_cuisines]
    short_cuisine_values.append(sum(cuisine_values[top_cuisines:]))
    short_cuisine_names = cuisine_clean_names[0:top_cuisines]
    short_cuisine_names.append(u'Others')

    plt.figure(figsize=(7, 7))
    explode = list(np.zeros(top_cuisines)) # explode the last slice ('Others')
    explode.append(0.08)

    wedgeprops={"edgecolor":"k", 'linewidth': 1} # edges properties

    plt.pie(short_cuisine_values, labels=short_cuisine_names, startangle=30,
            autopct='%1.1f%%', explode=explode, wedgeprops=wedgeprops)
    plt.title('Cuisines')
    plt.tight_layout()
    plt.axis('equal')
    plt.savefig(fig_file, bbox_inches='tight', dpi=1200)
    plt.close()

    # ===========
    # INGREDIENTS
    # ===========
    df['n_ingredients'] = df['ingredients'].str.len()

    # string manipulation of cuisine names
    cuisine_clean_names = clean_cuisine_names(df.cuisine.unique())

    # box plot number of ingredients
    fig_file = os.path.join(fig_path, 'ingredients_boxplot.pdf')
    plt.figure(figsize=(16, 6))
    ax = sns.boxplot(x='cuisine', y='n_ingredients', data=df)
    plt.ylabel('Number of Ingredients')
    plt.xlabel('Cuisine')
    plt.xticks(plt.xticks()[0], cuisine_clean_names)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=35)
    plt.savefig(fig_file, bbox_inches='tight', dpt=1200)
    plt.close()

    # counting ingredients from the entire dataset
    ingredients_count = ingredients_counter(df['ingredients'])

    # getting the top ingredients in the whole dataset
    top_common = 15
    top_ingredients_names = list(ingredients_count[:top_common].index)
    top_ingredients_values = list(ingredients_count[:top_common].values)

    # string manipulation of cuisine names
    cuisine_clean_names = clean_cuisine_names(top_ingredients_names)

    # top ingredients barplot
    fig_file = os.path.join(fig_path, 'top_ingredients_barplot.pdf')

    plt.figure(figsize=(10,7))
    sns.barplot(x=top_ingredients_values,
                y=cuisine_clean_names,
                edgecolor=(0,0,0),
                linewidth=1)
    plt.ylabel('Ingredients')
    plt.xlabel('Counts')
    plt.title('Top %i Most Used Ingredients' % int(top_common))
    plt.savefig(fig_file, bbox_inches='tight', dpi=1200)
    plt.close()
