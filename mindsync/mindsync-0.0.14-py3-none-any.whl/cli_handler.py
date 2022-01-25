import json


class CliHandler:
    def bind(self, api):
        self.__api = api


    def profile(self, args):
        api = self.__api
        self.__print_rv(api.profile(user_id=args.id), args)


    def set_profile(self, args):
        api = self.__api
        rv = api.set_profile(first_name=args.first_name, last_name=args.last_name, phone=args.phone,
                             gravatar=args.gravatar, nickname=args.nickname, wallet_symbol=args.wallet_symbol,
                             wallet_address=args.wallet_address, country=args.country, city=args.city)
        self.__print_rv(rv, args)
        

    def rigs_list(self, args):
        api = self.__api
        self.__print_rv(api.rigs_list(my=args.my), args)


    def rig_info(self, args):
        api = self.__api
        self.__print_rv(api.rig_info(rig_id=args.id), args)


    def set_rig(self, args):
        api = self.__api
        rv = api.set_rig(rig_id=args.id, enable=args.enable, power_cost=args.power_cost)
        self.__print_rv(rv, args)


    def rig_tariffs(self, args):
        api = self.__api
        self.__print_rv(api.rig_tariffs(rig_id=args.id), args)


    def rents_list(self, args):
        api = self.__api
        self.__print_rv(api.rents_list(my=args.my), args)


    def start_rent(self, args):
        api = self.__api
        rv = api.start_rent(rig_id=args.id, tariff_name=args.tariff)
        self.__print_rv(rv, args)


    def stop_rent(self, args):
        api = self.__api
        rv = api.stop_rent(rent_id=args.id)
        self.__print_rv(rv, args)


    def rent_state(self, args):
        api = self.__api
        rv = api.rent_state(rent_id=args.id)
        self.__print_rv(rv, args)


    def rent_info(self, args):
        api = self.__api
        rv = api.rent_info(rent_id=args.id)
        self.__print_rv(rv, args)


    def set_rent(self, args):
        api = self.__api
        rv = api.set_rent(rent_id=args.id, enable=args.enable, login=args.login, password=args.password)
        self.__print_rv(rv, args)


    @staticmethod
    def __print_rv(rv, args):
        if args.prettify:
            print(json.dumps(rv, indent=4, sort_keys=True))
        else:
            print(json.dumps(rv))
