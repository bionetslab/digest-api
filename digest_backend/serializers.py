from rest_framework import serializers


# class ExampleSerializer(serializers.ModelSerializer):
#     name = serializers.SerializerMethodField()
#     number = serializers.SerializerMethodField()
#
#     def get_name(self,obj):
#         return obj.name
#
#     def get_number(self,obj):
#         return obj.count
#
#     class Meta:
#         model = Example
#         fields = ['name', 'number']