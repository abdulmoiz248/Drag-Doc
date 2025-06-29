import pandas as pd

def merged_Dataset():
    df1 = pd.read_csv('datasets/combined_data.csv')      # label, text
    df2 = pd.read_csv('datasets/emails.csv')             # text, spam
    df3 = pd.read_csv('datasets/spam_assassin.csv')      # text, target
    df4 = pd.read_csv('datasets/spam.csv')               # Category, Message

    df1 = df1[['text', 'label']].rename(columns={'label': 'target'})
    df2 = df2[['text', 'spam']].rename(columns={'spam': 'target'})
    df3 = df3[['text', 'target']]

    df4 = df4[['Message', 'Category']].rename(columns={'Message': 'text', 'Category': 'target'})
    df4['target'] = df4['target'].map({'ham': 0, 'spam': 1})

    mergedDf = pd.concat([df1, df2, df3, df4], ignore_index=True)
    print("Column Names=", mergedDf.columns)
    print("Dataset Size=",mergedDf.size)
    return mergedDf

