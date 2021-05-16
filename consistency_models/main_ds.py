import driver
import eventual

def start_driver():
    # master = driver.Driver("linearizability")
    # master = driver.Driver("sequential")
    master = driver.Driver()
    master.start_execution()


if __name__ == "__main__":
    print("\n Starting test cases for Sequential Consistency")
    start_driver()
