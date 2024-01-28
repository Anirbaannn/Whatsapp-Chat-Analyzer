import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import seaborn as sns

st.set_page_config(page_title="WA Analyzer", page_icon="icon.png")

st.sidebar.title("Whatsapp Chat Analyzer")
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    #fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,df)

        #stats area
        st.title("Top Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        #timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user,df)
        plt.style.use('dark_background')
        fig,ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color ='blue')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        plt.style.use('dark_background')
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity mар
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            plt.style.use('dark_background')
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            plt.style.use('dark_background')
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color = 'orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title ('Activity Heatmap')
        user_heatmap = helper.activity_heatmap(selected_user,df)
        plt.style.use('dark_background')
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        #finding active users in group only
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x,new_df = helper.most_busy_users(df)

            col1, col2 = st.columns(2)

            with col1:
                plt.style.use('dark_background')
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color = 'red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        #wordcloud
        st.title('Word Cloud')
        df_wc = helper.create_wordcloud(selected_user,df)
        fig, ax= plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        #most common words
        most_common_df = helper.most_common_words(selected_user,df)
        fig,ax =plt.subplots()
        ax.barh(most_common_df[0],most_common_df[1], color = 'violet')
        st.title('Most Common Words')
        st.pyplot(fig)

        #emoji analysis
        emoji_df = helper.emoji_helper(selected_user,df)
        st.title("Emoji Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Emojis Count')
            # Display 'Percentage' column with 2 decimal places
            emoji_df_display = emoji_df[['Emoji', 'Count', 'Percentage']]
            emoji_df_display['Percentage'] = emoji_df_display['Percentage'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(emoji_df_display)
        with col2:
            st.subheader('Top Emojis')

            # Set the emoji font
            plt.rcParams['font.family'] = helper.emoji_font.get_name()

            # Create the pie chart with enhanced features
            fig, ax = plt.subplots()
            plt.style.use('dark_background')

            wedges, texts, autotexts = ax.pie(
                emoji_df['Count'].head(),  # Use 'Count' column for consistency
                labels=emoji_df['Emoji'].head().tolist(),
                autopct='%1.1f%%',  # Dynamic percentage formatting
                textprops={'fontproperties': helper.emoji_font},  # Ensure emoji rendering
                pctdistance=1 - 0.65  # Adjust label placement as needed
            )
            # Customize label appearance (optional)
            plt.setp(autotexts, fontsize=10, weight="bold")
            plt.axis('equal')  # Ensure circular pie chart
            st.pyplot(fig)