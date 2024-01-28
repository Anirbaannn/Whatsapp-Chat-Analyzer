from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import matplotlib.font_manager as font_manager
from collections import Counter
import emoji

emoji_font_path = "TwitterColorEmoji-SVGinOT.ttf"  # Adjust path if needed
emoji_font = font_manager.FontProperties(fname=emoji_font_path)

extract = URLExtract()
def fetch_stats(selected_user,df):

    if selected_user != 'Overall':
        #for specific user
        #fetch no. of messages
        df = df[df['user'] == selected_user]
        num_messages = df.shape[0]
        #fetch no. of words
        words = []
        for message in df['message']:
            words.extend(message.split())
        #fetch no.of media
        num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
        #fetch no. of links
        links = []
        for message in df['message']:
            links.extend(extract.find_urls(message))
        return num_messages, len(words), num_media_messages, len(links)
    else:
        #for group
        num_messages = df.shape[0]
        words = []
        for message in df['message']:
            words.extend(message.split())
        num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
        links = []
        for message in df['message']:
            links.extend(extract.find_urls(message))
        return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(columns={'index': 'Name', 'user':'Percentage'})
    return x,df

def create_wordcloud(selected_user,df):

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='black')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user,df):

    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend(c for c in message if c in emoji.EMOJI_DATA)


    emoji_df = pd.DataFrame({'Emoji': emojis, 'Count': [Counter(emojis)[emoji] for emoji in emojis]})
    emoji_df = emoji_df.groupby('Emoji')['Count'].sum().reset_index()


    # Sort DataFrame by 'Count' column in descending order
    emoji_df = emoji_df.sort_values(by='Count', ascending=False)

    # Calculate the percentage column
    total_emojis = emoji_df['Count'].sum()
    emoji_df['Percentage'] = (emoji_df['Count'] / total_emojis) * 100

    # Sort DataFrame by 'Count' column in descending order
    emoji_df = emoji_df.sort_values(by='Count', ascending=False)

    return emoji_df


def monthly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap