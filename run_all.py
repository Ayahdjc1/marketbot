# run_all.py

import subprocess
import sys
import os
import time
import signal
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def launch_process(name: str, path: str) -> subprocess.Popen:
    """Запускает процесс с логированием"""
    logger.info(f"🚀 Запуск: {name}")
    try:
        return subprocess.Popen(
            [sys.executable, path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
    except Exception as e:
        logger.error(f"❌ Ошибка запуска {name}: {str(e)}")
        raise

def monitor_process(proc: subprocess.Popen, name: str) -> None:
    """Мониторинг вывода процесса"""
    while True:
        output = proc.stdout.readline()
        if output == '' and proc.poll() is not None:
            break
        if output:
            logger.info(f"[{name}] {output.strip()}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    processes = []

    try:
        # Запуск процессов
        collector_proc = launch_process("Сборщик данных", os.path.join(BASE_DIR, 'collector.py'))
        bot_proc = launch_process("Телеграм-бот", os.path.join(BASE_DIR, 'bot.py'))

        processes = [collector_proc, bot_proc]

        # Запуск мониторинга вывода
        import threading
        threading.Thread(target=monitor_process, args=(collector_proc, "COLLECTOR"), daemon=True).start()
        threading.Thread(target=monitor_process, args=(bot_proc, "BOT"), daemon=True).start()

        logger.info("✅ Все компоненты запущены. Для выхода нажмите Ctrl+C")

        # Бесконечное ожидание с проверкой статуса
        while True:
            time.sleep(1)
            for proc in processes:
                if proc.poll() is not None:
                    logger.error(f"⚠️ Процесс {proc.pid} завершился неожиданно!")
                    raise RuntimeError("Один из процессов завершился")

    except (KeyboardInterrupt, RuntimeError):
        logger.info("\n🛑 Инициирована остановка процессов...")
        for proc in processes:
            if proc.poll() is None:
                try:
                    os.kill(proc.pid, signal.SIGTERM)
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning("⚠️ Принудительное завершение процесса...")
                    os.kill(proc.pid, signal.SIGKILL)
                except Exception as e:
                    logger.error(f"Ошибка при остановке процесса: {str(e)}")
        
        logger.info("🧹 Все процессы остановлены")

    except Exception as e:
        logger.error(f"🔥 Критическая ошибка: {str(e)}")
        sys.exit(1)
