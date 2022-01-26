from property_price_register.models.sale import Sales


def main():

    sales = Sales.load()

    print('Loaded %s sales' % (len(sales)))
    print('Do something with the data in the variable \'sales\'...')

    import pdb; pdb.set_trace()

    pass


if __name__ == '__main__':
    main()
