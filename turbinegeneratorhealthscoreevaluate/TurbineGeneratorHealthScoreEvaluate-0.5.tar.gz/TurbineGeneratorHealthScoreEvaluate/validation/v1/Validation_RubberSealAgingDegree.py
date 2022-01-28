def main():
	for i in range(2000, 2051, 1):
		print(i, RubberSealAgingDegree(sinceYear=2000, nowYear=i, designLife=20).agingDegree)

if __name__ == '__main__':
    main()
