# utils/scheduler.py
import threading
import time
from datetime import datetime, timedelta
from utils.jwt_utils import cleanup_expired_tokens

class SimpleScheduler:
    '''Планировщик ежедневного обслуживания и удаления устаревших токенов из черного списка'''
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_cleanup = None
        self.last_maintenance = None
        
    def should_run_cleanup(self) -> bool:
        """Проверяет, нужно ли запускать очистку (каждый час)"""
        if self.last_cleanup is None:
            return True
        return datetime.now() - self.last_cleanup > timedelta(minutes=5)
    
    def should_run_maintenance(self) -> bool:
        """Проверяет, нужно ли запускать ежедневное обслуживание (каждый день в 2:00)"""
        now = datetime.now()
        if self.last_maintenance is None:
            return now.hour >= 2  # Запускаем если сейчас после 2:00
        return now.hour == 2 and now.date() > self.last_maintenance.date()
    
    def run_cleanup(self) -> None:
        """Запуск очистки черного списка"""
        try:
            cleaned_count = cleanup_expired_tokens()
            self.last_cleanup = datetime.now()
            if cleaned_count > 0:
                print(f"[{self.last_cleanup}] Очищено {cleaned_count} токенов из черного списка")
            else:
                print('Токенов для очистки не найдено')
        except Exception as e:
            print(f"[{datetime.now()}] Ошибка при очистке черного списка: {e}")
    
    def run_maintenance(self) -> None:
        """Запуск ежедневного обслуживания"""
        try:
            self.last_maintenance = datetime.now()
            print(f"[{self.last_maintenance}] Выполнение ежедневного обслуживания")
            # Дополнительные задачи обслуживания можно добавить здесь
        except Exception as e:
            print(f"[{datetime.now()}] Ошибка при ежедневном обслуживании: {e}")
    
    def run_scheduler(self) -> None:
        """Основной цикл планировщика"""
        self.running = True
        print("Фоновый планировщик запущен")
        
        while self.running:
            try:
                # Проверяем и выполняем задачи
                if self.should_run_cleanup():
                    self.run_cleanup()
                
                if self.should_run_maintenance():
                    self.run_maintenance()
                
                # Ждем 1 минуту перед следующей проверкой
                time.sleep(60)
                
            except Exception as e:
                print(f"Ошибка в планировщике: {e}")
                time.sleep(300)  # При ошибке ждем 5 минут
    
    def start(self) -> None:
        """Запуск планировщика"""
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.thread.start()
    
    def stop(self) -> None:
        """Остановка планировщика"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=10)

# Глобальный экземпляр
scheduler = SimpleScheduler()

def start_cleanup_scheduler() -> SimpleScheduler:
    """Функция для запуска планировщика"""
    scheduler.start()
    return scheduler