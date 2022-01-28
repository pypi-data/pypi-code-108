import gazu
from kabaret import flow

from libreflow import baseflow


class EntityType(flow.values.ChoiceValue):

    CHOICES = ["Assets", "Episodes"]


class SyncFromKitsu(baseflow.kitsu.SyncFromKitsu):

    ICON = ("icons.libreflow", "sync_arrow")

    entity_type = flow.Param("Assets", EntityType)
    from_index = flow.IntParam().ui(hidden=True)
    to_index = flow.IntParam().ui(hidden=True)

    def run(self, button):
        if button == "Cancel":
            return

        project = self.root().project()
        project_kitsu_id = project.kitsu_id.get()

        if self.entity_type.get() == "Episodes":
            kitsu_episodes = gazu.shot.all_episodes_for_project(project_kitsu_id)
            episodes = project.episodes

            # Pull episodes
            for kitsu_episode in kitsu_episodes:
                try:
                    episode = episodes.add(kitsu_episode["name"])
                except ValueError:
                    episode = episodes[kitsu_episode["name"]]

                episode_id = kitsu_episode["id"]
                episode.kitsu_id.set(episode_id)
                episode.update_kitsu_settings()

                # Pull sequences
                kitsu_sequences = gazu.shot.all_sequences_for_episode(episode_id)
                sequences = episode.sequences

                for kitsu_sequence in kitsu_sequences:
                    try:
                        sequence = sequences.add(kitsu_sequence["name"])
                    except ValueError:
                        sequence = sequences[kitsu_sequence["name"]]

                    sequence_id = kitsu_sequence["id"]
                    sequence.kitsu_id.set(sequence_id)
                    sequence.description.set(kitsu_sequence["description"])
                    sequence.update_kitsu_settings()

                    # Pull shots
                    kitsu_shots = gazu.shot.all_shots_for_sequence(sequence_id)
                    shots = sequence.shots

                    for kitsu_shot in kitsu_shots:
                        try:
                            shot = shots.add(kitsu_shot["name"])
                        except ValueError:
                            shot = shots[kitsu_shot["name"]]

                        shot.kitsu_id.set(kitsu_shot["id"])
                        shot.description.set(kitsu_shot["description"])
                        shot.update_kitsu_settings()

                    shots.touch()

                sequences.touch()

            episodes.touch()

        elif self.entity_type.get() == "Assets":
            kitsu_assets = gazu.asset.all_assets_for_project(project_kitsu_id)
            asset_types = project.asset_lib.asset_types

            for kitsu_asset in kitsu_assets:
                kitsu_asset = gazu.asset.get_asset(kitsu_asset["id"])
                asset_type_name = kitsu_asset["asset_type_name"]
                asset_name = kitsu_asset["name"]

                try:
                    asset_type = asset_types.add(asset_type_name)
                except ValueError:
                    asset_type = asset_types[asset_type_name]

                assets = asset_type.assets

                try:
                    asset = assets.add(asset_name)
                except ValueError:
                    asset = assets[asset_name]

                asset.kitsu_id.set(kitsu_asset["id"])
                asset.description.set(kitsu_asset["description"])
                asset.update_kitsu_settings()

            asset_types.touch()


class KitsuEpisode(baseflow.kitsu.KitsuObject):
    def kitsu_dict(self):
        return gazu.shot.get_episode(self.kitsu_id.get())

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_url:
            child_value.set(
                "%s/episodes/%s/shots"
                % (self.root().project().kitsu_url.get(), self.kitsu_id.get())
            )
