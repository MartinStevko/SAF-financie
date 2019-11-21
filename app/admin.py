from django.contrib import admin


class OrderedAdminSite(admin.AdminSite):

    def get_app_list(self, request):
        app_ordering = {
            'autentifikácia a autorizácia': 1,
            'financie': 2,
            'faktúry': 3,
        }

        model_ordering = [{
            'používatelia': 1,
            'oprávnenia': 2,
            'skupiny': 3,
        }, {
            'polozka': 1,
        }, {
            'polozka': 1,
        }]

        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: app_ordering[x['name'].lower()])

        for i in range(len(app_list)):
            app_list[i]['models'].sort(
                key=lambda x: model_ordering[i][x['name'].lower()]
            )

        return app_list
