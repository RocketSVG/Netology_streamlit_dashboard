import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
st.set_page_config(layout="wide")

@st.cache_data
def load_data():                                                                                                          #2.2 Функция для создания датафреймов из файлов .csv Так же сосздаем title и делаем заголовок для таблицы
    df_items = pd.read_csv('Data/items.csv')
    df_orders = pd.read_csv('Data/orders.csv')
    df_users = pd.read_csv('Data/users.csv')
    return df_items, df_orders, df_users

items, orders, users = load_data()
st.title('Магазин "Жёваный крот"')

df1 = pd.merge(orders, users, on="user_id", how="left")                                                                    #2.3 Соединяем таблицы, через левое соединение и указанные в задании ключи.
df_boss = pd.merge(df1, items, on="item_id", how="left")
#st.subheader('Данные')


qty_missed = df_boss.isnull().sum()                                                                                        #2.4 Проверяем на наличие пропусков (пропусков нет). Далее проверяем типы данных в столбцах с числовыми значениями.Приводим столбцы с датами к типу datetime
#st.write('Проверка пропусков:')
#st.write(qty_missed)
df_boss['order_date'] = pd.to_datetime(df_boss['order_date'])
df_boss['registration_date'] = pd.to_datetime(df_boss['registration_date'])
#st.write(df_boss.dtypes)

pad1, pad2, pad3, pad4 = st.tabs(["Сырые данные", "Ключевые показатели", "Визуализация", "Аналитические выводы"])               #Создаём список вкладок
with pad1:                                                                                                                      #Первая ыкладка с сфрыми данными
    st.header("Объеденённые сырые данные")
    st.dataframe(df_boss)                                                                                                      # 5.1 Показываем итоговый датафрейм
    with st.sidebar:                                                                                                           # Sidebar, чтобы вынести фильтры в левую часть экрана.
        st.header("Фильтры")                                                                                                   # Делаем заголовки
        vib_chb_date = st.checkbox("По дате")                                                                                 # Создаём две переменные с флагами для включения фильтров
        vib_chb_cat = st.checkbox("По категории")
        vib_date = st.selectbox("Выберите дату", options=df_boss['order_date'].dt.date.unique())                        #Создаём первый фильтр по дате заказа(уникальный)
        vib_cat = st.selectbox("Выберите категорию", options=df_boss['category'].unique())                               # Создаём второй фильтр по категории, тут уникальность по значению
    filtered_df = df_boss
    if vib_chb_date:                                                                                                            #Если пользователь поставил галочку в фильтре с датой - то будет производится фильтрация, тоже самое с категорией.
        filtered_df = filtered_df[filtered_df['order_date'].dt.date == vib_date]
    if vib_chb_cat:
        filtered_df = filtered_df[filtered_df['category'] == vib_cat]
    st.subheader("Данные после применения фильтров")
    st.dataframe(filtered_df)

with pad2:                                                                                                                      #Вкладка с ключевыми показателями
    st.header("Ключевые показатели")
    qty_raws = len(filtered_df)
    filtered_df["revenue"] = filtered_df["quantity"] * filtered_df["price_per_unit"]                                            #Подсчитываем общую сумму перемножая стоимость товара на количество проданного
    avg_revenue = round(sum(filtered_df["revenue"])/qty_raws, 2)                                                                #Считаем среднее разделив общуюю сумму по продажам на общее количество продаж
    col1, col2 = st.columns(2)                                                                                                  #Будем отображать в два столбца
    with col1:                                                                                                                  #В первом столбце покажем количество заказов и выручку
        st.metric("Количество заказов: ", qty_raws)
        st.metric("Выручка: ", round(sum(filtered_df["revenue"]), 2))
    with col2:                                                                                                                  #Во втором столбце покажем количество уникальных пользователей и средний чек по заказам
        st.metric("Количество уникальных пользователей: ", len(filtered_df["user_id"].unique()))
        st.metric("Средний чек по заказам:", avg_revenue)
with pad3:                                                                                                                      #Третья вкладка с визуализацией
    st.header("Визуализация")
    top10_goods = filtered_df.groupby('item_name')['revenue'].sum().sort_values(ascending=False).head(10)                       #Считаем топ-10 выручки по товарам
    fig, ax = plt.subplots()                                                                                                    #Строим первую визуализацию и выводим топ 10 стоимости по проданным товарам
    figure1 = ax.barh(top10_goods.index, top10_goods.values, color='green', edgecolor='darkgreen')
    ax.bar_label(figure1, fmt='%.0f')
    ax.set_title("Топ-10 товаров по выручке")
    st.pyplot(fig)
    plt.close()
    fig, ax = plt.subplots()                                                                                                    #Строим вторую визуализацию по доле продаж по категориям
    revenue_cat = filtered_df.groupby('category')['revenue'].sum()                                                              #Группируем все продажи по категории и считаем сумму
    ax.pie(revenue_cat.values, labels=revenue_cat.index, autopct='%1.1f%%')
    ax.set_title("Доля выручки по категориям")
    st.pyplot(fig)
    plt.close()
    fig, ax = plt.subplots()                                                                                                    #Третья визуализация, количесвто продаж по дням недели
    weekday_orders = filtered_df['order_date'].dt.weekday.value_counts().sort_index()                                           #Раскладываем по индексу дни недели и смотрим сколько было продаж в каждом индексе
    bars = ax.bar(weekday_orders.index, weekday_orders.values, color='green')
    ax.bar_label(bars)
    ax.set_title("Количество заказов по дням недели")
    ax.set_xlabel("0-Пн,6-Сб")
    ax.set_ylabel("Количество заказов")
    st.pyplot(fig)
    plt.close()
with pad4:                                                                                                                      #Четвертая вкладка с выводами. Используем markdown и прописываем выводы смотря в нашу визуализацию
    st.markdown("""
    **Выводы на основе проведённом анализе:**
    \n**Вывод 1:** Более 50% выручки принесла категория "Электроника", затем категория "Бытовая техника" - более 10%.
    \n**Вывод 2:** Наибольшее количество заказов пришлось на вторую половину недели. В четверг - 7, в пятницу - 9, в субботу - 7. В остальные дни было по 4 заказа.
    \n**Вывод 3:** Наибольшая выручка по товару "Ноутбук Asus VivoBook" - 14995.
    """)




