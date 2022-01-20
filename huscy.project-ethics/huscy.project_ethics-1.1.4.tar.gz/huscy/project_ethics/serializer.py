from rest_framework import serializers

from huscy.project_ethics import models, services


class EthicBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EthicBoard
        fields = 'id', 'name'

    def create(self, validated_data):
        return services.create_ethic_board(**validated_data)

    def update(self, ethic_board, validated_data):
        return services.update_ethic_board(ethic_board, **validated_data)


class EthicsFileSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(required=False, default='')
    filetype_name = serializers.CharField(source='get_filetype_display', read_only=True)

    class Meta:
        model = models.EthicFile
        fields = (
            'id',
            'ethic',
            'filehandle',
            'filename',
            'filetype',
            'filetype_name',
            'uploaded_at',
            'uploaded_by',
        )

    def create(self, validated_data):
        return services.create_ethic_file(**validated_data)


class UpdateEthicsFileSerializer(EthicsFileSerializer):
    filename = serializers.CharField()

    class Meta:
        model = models.EthicFile
        fields = 'id', 'ethic', 'filename', 'filetype', 'filetype_name'

    def update(self, ethics_file, validated_data):
        return services.update_ethic_file(ethics_file, **validated_data)


class EthicSerializer(serializers.ModelSerializer):
    ethic_board_name = serializers.CharField(source='ethic_board.name', read_only=True)
    ethic_files = EthicsFileSerializer(many=True, read_only=True)

    class Meta:
        model = models.Ethic
        fields = 'code', 'ethic_board', 'ethic_board_name', 'ethic_files', 'id', 'project'
        read_only_fields = 'project',

    def create(self, validated_data):
        return services.create_ethic(**validated_data)

    def update(self, ethic, validated_data):
        return services.update_ethic(ethic, **validated_data)
