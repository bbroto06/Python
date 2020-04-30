#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import math
import string
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# # Follow this post : https://www.analyticsvidhya.com/blog/2020/04/beginners-guide-exploratory-data-analysis-text-data/?utm_source=feedburner&utm_medium=email&utm_campaign=Feed%3A+AnalyticsVidhya+%28Analytics+Vidhya%29

# ### Read data

# In[2]:


df = pd.read_csv("1429_1.csv")
print(df.shape)


# In[3]:


df = df[['name', 'reviews.text', 'reviews.doRecommend', 'reviews.numHelpful']]
print(df.shape)


# In[4]:


df.isnull().sum() # Count of null throughout


# In[5]:


df.dropna(inplace=True) # Drop rows if they contain NA in any column
df.isnull().sum()
print(df.shape)


# ### Clean data

# In[6]:


df = df.groupby('name').filter( lambda x:len(x) > 500 ).reset_index(drop=True) # Considering only those products that have more than 500 reviews
print('Number of products=>', len(df['name'].unique()) )
print(df.shape)


# In[7]:


df['reviews.doRecommend'] = df['reviews.doRecommend'].astype(int) # Change float type to int
df['reviews.numHelpful'] = df['reviews.numHelpful'].astype(int)
print(df.shape)


# In[8]:


df.head()


# In[9]:


print(df['name'].unique())


# In[10]:


df['name'] = df['name'].apply(lambda x: x.split(',,,')[0]) # Remove ,,, and repeatitions
print(df['name'].unique())


# In[11]:


# Print 5 random reviews
for index, text in enumerate( df['reviews.text'][35:40] ):
    print('Review %d:\n' % (index+1), text )


# In[12]:


# Dictionary of English Contractions
contractions_dict = {"ain't": "are not",
                     "'s":" is",
                     "aren't": "are not",
                     "can't": "cannot",
                     "can't've": "cannot have",
                     "'cause": "because",
                     "could've": "could have",
                     "couldn't": "could not",
                     "couldn't've": "could not have", 
                     "didn't": "did not",
                     "doesn't": "does not",
                     "don't": "do not",
                     "hadn't": "had not",
                     "hadn't've": "had not have",
                     "hasn't": "has not",
                     "haven't": "have not",
                     "he'd": "he would",
                     "he'd've": "he would have",
                     "he'll": "he will", 
                     "he'll've": "he will have",
                     "how'd": "how did",
                     "how'd'y": "how do you",
                     "how'll": "how will",
                     "I'd": "I would", 
                     "I'd've": "I would have",
                     "I'll": "I will",
                     "I'll've": "I will have",
                     "I'm": "I am",
                     "I've": "I have", 
                     "isn't": "is not",
                     "it'd": "it would",
                     "it'd've": "it would have",
                     "it'll": "it will",
                     "it'll've": "it will have", 
                     "let's": "let us",
                     "ma'am": "madam",
                     "mayn't": "may not",
                     "might've": "might have",
                     "mightn't": "might not", 
                     "mightn't've": "might not have",
                     "must've": "must have",
                     "mustn't": "must not",
                     "mustn't've": "must not have", 
                     "needn't": "need not",
                     "needn't've": "need not have",
                     "o'clock": "of the clock",
                     "oughtn't": "ought not",
                     "oughtn't've": "ought not have",
                     "shan't": "shall not",
                     "sha'n't": "shall not",
                     "shan't've": "shall not have",
                     "she'd": "she would",
                     "she'd've": "she would have",
                     "she'll": "she will", 
                     "she'll've": "she will have",
                     "should've": "should have",
                     "shouldn't": "should not", 
                     "shouldn't've": "should not have",
                     "so've": "so have",
                     "that'd": "that would",
                     "that'd've": "that would have", 
                     "there'd": "there would",
                     "there'd've": "there would have", 
                     "they'd": "they would",
                     "they'd've": "they would have",
                     "they'll": "they will",
                     "they'll've": "they will have", 
                     "they're": "they are",
                     "they've": "they have",
                     "to've": "to have",
                     "wasn't": "was not",
                     "we'd": "we would",
                     "we'd've": "we would have",
                     "we'll": "we will",
                     "we'll've": "we will have",
                     "we're": "we are",
                     "we've": "we have", 
                     "weren't": "were not",
                     "what'll": "what will",
                     "what'll've": "what will have",
                     "what're": "what are", 
                     "what've": "what have",
                     "when've": "when have",
                     "where'd": "where did", 
                     "where've": "where have",
                     "who'll": "who will",
                     "who'll've": "who will have",
                     "who've": "who have",
                     "why've": "why have",
                     "will've": "will have",
                     "won't": "will not",
                     "won't've": "will not have", 
                     "would've": "would have",
                     "wouldn't": "would not",
                     "wouldn't've": "would not have",
                     "y'all": "you all", 
                     "y'all'd": "you all would",
                     "y'all'd've": "you all would have",
                     "y'all're": "you all are",
                     "y'all've": "you all have", 
                     "you'd": "you would",
                     "you'd've": "you would have",
                     "you'll": "you will",
                     "you'll've": "you will have", 
                     "you're": "you are",
                     "you've": "you have"}


# In[13]:


# Regular expression for finding contractions
contractions_re = re.compile( '(%s)' % '|'.join( contractions_dict.keys() ) )


# In[14]:


# Function for expanding contractions
def expand_contractions(text, contractions_dict=contractions_dict ):
    def replace(match):
        return contractions_dict[match.group(0)]
    return contractions_re.sub(replace, text)


# In[15]:


# Expanding Contractions in the reviews
df['reviews.text'] = df['reviews.text'].apply(lambda x: expand_contractions(x) )


# In[16]:


# Lowercase the reviews
df['cleaned'] = df['reviews.text'].apply(lambda x: x.lower() )


# In[17]:


# Remove digits and words containing digits
df['cleaned'] = df['cleaned'].apply(lambda x: re.sub('\w*\d\w*', '', x) )


# In[18]:


# Remove Punctuations
df['cleaned'] = df['cleaned'].apply(lambda x: re.sub('[%s]' % re.escape(string.punctuation), '', x) )


# In[19]:


# Removing extra spaces
df['cleaned'] = df['cleaned'].apply(lambda x: re.sub(' +', ' ', x) )


# In[20]:


# Print 5 random reviews
for index, text in enumerate(df['cleaned'][35:40]):
    print( 'Review %d:\n' % (index+1), text )


# ### Preparing Text Data for Exploratory Data Analysis (EDA)

# # https://stackoverflow.com/questions/38368318/installing-a-pip-package-from-within-a-jupyter-notebook-not-working/50473278#50473278

# #### Install a pip package in the current Jupyter kernel
# ###### import sys
# ###### !{sys.executable} -m pip install spacy

# In[21]:


import spacy


# In[22]:


# Loading model
nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'] )


# # https://stackoverflow.com/questions/49964028/spacy-oserror-cant-find-model-en

# In[23]:


# Lemmatization with stopwords removal
df['lemmatized'] = df['cleaned'].apply(lambda x: ' '.join( [token.lemma_ for token in list(nlp(x)) if (token.is_stop==False)]) )


# In[24]:


# Print 5 random reviews
for index, text in enumerate(df['lemmatized'][35:40]):
    print( 'Review %d:\n' % (index+1), text )


# In[25]:


# Group them according to products
df_grouped = df[['name','lemmatized']].groupby(by='name').agg(lambda x:' '.join(x))
df_grouped.head()


# In[26]:


df_grouped.shape


# In[27]:


# Creating Document Term Matrix
from sklearn.feature_extraction.text import CountVectorizer 

cv = CountVectorizer(analyzer='word')
data = cv.fit_transform(df_grouped['lemmatized'])
df_dtm = pd.DataFrame(data.toarray(), columns=cv.get_feature_names())
df_dtm.index = df_grouped.index
df_dtm.head()


# In[28]:


df_dtm.to_csv('temp_del.csv')


# ## Generate Word Cloud

# #### Install a pip package in the current Jupyter kernel
# ##### import sys
# ##### !{sys.executable} -m pip install wordcloud

# In[29]:


# Importing wordcloud for plotting word clouds and textwrap for wrapping longer text
from wordcloud import WordCloud
from textwrap import wrap


# In[30]:


# Function for generating word clouds
def generate_wordcloud(data, title):
    wc = WordCloud(width=400, height=330, max_words=150,colormap="Dark2").generate_from_frequencies(data)
    plt.figure(figsize=(10,8))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.title('\n'.join(wrap(title,60)),fontsize=13)
    plt.show()


# In[31]:


# Transposing document term matrix
df_dtm = df_dtm.transpose()


# In[32]:


# Plotting word cloud for each product
for index, product in enumerate(df_dtm.columns):
    generate_wordcloud(df_dtm[product].sort_values(ascending=False), product )


# ### Sentiment Analysis for Amazon products

# #### Install a pip package in the current Jupyter kernel
# ##### import sys
# ##### !{sys.executable} -m pip install textblob

# In[33]:


from textblob import TextBlob
df['polarity'] = df['lemmatized'].apply(lambda x: TextBlob(x).sentiment.polarity )


# In[34]:


print("3 Random Reviews with Highest Polarity:")
for index, review in enumerate(df.iloc[df['polarity'].sort_values(ascending=False)[:3].index]['reviews.text']):
    print('Review {}:\n'.format(index+1), review)


# In[35]:


print("3 Random Reviews with Lowest Polarity:")
for index, review in enumerate(df.iloc[df['polarity'].sort_values(ascending=True)[:3].index]['reviews.text']):
    print('Review {}:\n'.format(index+1), review)


# ### Plot polarities of reviews for each product and compare them

# In[36]:


product_polarity_sorted = pd.DataFrame(df.groupby('name')['polarity'].mean().sort_values(ascending=True))

plt.figure(figsize=(16,8))
plt.xlabel('Polarity')
plt.ylabel('Products')
plt.title('Polarity of Different Amazon Product Reviews')
polarity_graph = plt.barh(np.arange(len(product_polarity_sorted.index)),product_polarity_sorted['polarity'],color='purple',)

# Writing product names on bar
for bar,product in zip(polarity_graph,product_polarity_sorted.index):
  plt.text(0.005,bar.get_y()+bar.get_width(),'{}'.format(product), va='center', fontsize=11, color='white')

# Writing polarity values on graph
for bar, polarity in zip(polarity_graph,product_polarity_sorted['polarity']):
  plt.text(bar.get_width()+0.001, bar.get_y()+bar.get_width(), '%.3f'%polarity, va='center', fontsize=11, color='black')
  
plt.yticks([])
plt.show()


# ### Plot recommendations of products

# In[37]:


recommend_percentage = pd.DataFrame(((df.groupby('name')['reviews.doRecommend'].sum()*100)/df.groupby('name')['reviews.doRecommend'].count()).sort_values(ascending=True))

plt.figure(figsize=(16,8))
plt.xlabel('Recommend Percentage')
plt.ylabel('Products')
plt.title('Percentage of reviewers recommended a product')
recommend_graph = plt.barh(np.arange(len(recommend_percentage.index)),recommend_percentage['reviews.doRecommend'],color='green')

# Writing product names on bar
for bar, product in zip(recommend_graph,recommend_percentage.index):
  plt.text(0.5,bar.get_y()+0.4,'{}'.format(product), va='center', fontsize=11, color='white')

# Writing recommendation percentage on graph
for bar,percentage in zip(recommend_graph,recommend_percentage['reviews.doRecommend']):
  plt.text(bar.get_width()+0.5, bar.get_y()+0.4, '%.2f'%percentage, va='center', fontsize=11, color='black')

plt.yticks([])
plt.show()


# ### Readability of reviews upvoted as helpful by others

# #### Install a pip package in the current Jupyter kernel
# ##### import sys
# ##### !{sys.executable} -m pip install textstat

# In[38]:


import textstat


# In[39]:


df['dale_chall_score'] = df['reviews.text'].apply(lambda x: textstat.dale_chall_readability_score(x))
df['flesh_reading_ease'] = df['reviews.text'].apply(lambda x: textstat.flesch_reading_ease(x))
df['gunning_fog'] = df['reviews.text'].apply(lambda x: textstat.gunning_fog(x))

print('Dale Chall Score of upvoted reviews=>',df[df['reviews.numHelpful']>1]['dale_chall_score'].mean())
print('Dale Chall Score of not upvoted reviews=>',df[df['reviews.numHelpful']<=1]['dale_chall_score'].mean())

print('Flesch Reading Score of upvoted reviews=>',df[df['reviews.numHelpful']>1]['flesh_reading_ease'].mean())
print('Flesch Reading Score of not upvoted reviews=>',df[df['reviews.numHelpful']<=1]['flesh_reading_ease'].mean())

print('Gunning Fog Index of upvoted reviews=>',df[df['reviews.numHelpful']>1]['gunning_fog'].mean())
print('Gunning Fog Index of not upvoted reviews=>',df[df['reviews.numHelpful']<=1]['gunning_fog'].mean())


# ## text_standard() function
# ### uses various readability checking formulas, 
# ### combines the result and 
# ### returns the grade of education required to understand a particular document completely.

# In[40]:


df['text_standard'] = df['reviews.text'].apply(lambda x: textstat.text_standard(x) )

print('Text Standard of upvoted reviews=>', df[df['reviews.numHelpful']>1]['text_standard'].mode() )
print('Text Standard of not upvoted reviews=>', df[df['reviews.numHelpful']<=1]['text_standard'].mode() )


# ## reading_time() function
# ### takes a piece of text as an argument and 
# ### returns the reading time for it in seconds.

# In[41]:


df['reading_time'] = df['reviews.text'].apply(lambda x: textstat.reading_time(x) )

print('Reading Time of upvoted reviews=>', df[df['reviews.numHelpful']>1]['reading_time'].mean() )
print('Reading Time of not upvoted reviews=>', df[df['reviews.numHelpful']<=1]['reading_time'].mean() )

