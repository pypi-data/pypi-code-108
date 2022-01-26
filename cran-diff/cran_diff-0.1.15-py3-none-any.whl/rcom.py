from rpy2.robjects.packages import importr
import rpy2.rinterface
import rpy2.robjects as ro


class RCom:
    def __init__(self):
        rpy2.rinterface.initr()
        utils = importr("utils")  # noqa
        self.check_packages(["readr", "utils"])

    def check_packages(self, packages):
        for p in packages:
            x = ro.r(f'require("{p}")')
            if not x[0]:
                raise Exception(f"Package {p} not available in R session")

    def write_news(self, package, version, lib_loc):
        r_str_assign = f"y = utils::news(package = '{package}', lib.loc = '{lib_loc}')"
        file_location = f"{lib_loc}/{package}_{version}.csv"
        r_str_write = f"if(length(y) != 0) readr::write_csv(y, '{file_location}')"
        # print(r_str_assign)
        # print(r_str_write)
        try:
            ro.r(r_str_assign)
            # print("package ", ro.r('length(y)'))
            ro.r(r_str_write)
        except Exception as e:
            print(f"{package} {version}")
            print(e)
        return file_location

    def write_exports(self, package, version, lib_loc):
        r_str_assign = (
            f"y = parseNamespaceFile(package = '{package}', package.lib = '{lib_loc}')"
        )
        r_str_s3names = "s3names = paste(y$S3methods[,1], y$S3methods[,2], sep = '.')"
        r_str_join_names = (
            "names = c(y$exports, y$exportPatterns, y$exportMethods,"
            + " y$exportClasses, y$exportClassPatterns, s3names)"
        )
        r_str_join_types = (
            "types = c(rep('function', times = length(y$exports)),"
            + " rep('pattern', times = length(y$exportPatterns)),"
            + " rep('S4method', times = length(y$exportMethods)),"
            + " rep('S4class', times = length(y$exportClasses)),"
            + " rep('S4class', times = length(y$exportClassPatterns)),"
            + " rep('S3method', times = length(s3names)))"
        )
        r_str_form_result = "result = data.frame(name = names, type = types)"
        file_location = f"{lib_loc}/{package}_{version}_exports.csv"
        r_str_write = (
            f"if(nrow(result) != 0) readr::write_csv(result, '{file_location}')"
        )
        try:
            ro.r(r_str_assign)
            ro.r(r_str_s3names)
            ro.r(r_str_join_names)
            ro.r(r_str_join_types)
            ro.r(r_str_form_result)
            ro.r(r_str_write)
        except Exception as e:
            print(f"{package} {version}")
            print(e)
        return file_location
