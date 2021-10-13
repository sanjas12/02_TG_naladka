class Myclass():            # Создаем объект класса
    def sayhello(self, n):    # Создаем метод класс,
        print('Чета делаем в первом методе!')
        self.number = n
    def get(self):          # Создаем другой метод класса
        print('выводим', self.number)
    def __init__(self):     # создаем конструктор который автоматически инициализирует экземпляр класса
        self.number = 10  # или так

obj = Myclass()         # Создаем экземпляр класса
obj.get()               # Вызываем метод get класса Myclass
# obj.sayhello(23)
obj.get()

# i = 0
# for zz in range (10):
#     obj.sayhello(i)          # вызываем медот класса Myclass
#     obj.get()
#     i = i+1
