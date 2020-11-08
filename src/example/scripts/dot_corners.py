from enginelib.script import Script
from enginelib.script import on_frame


class DotCorners(Script):
    def __init__(self, enabled=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enabled = enabled

    @on_frame(always_fire=True)
    def update_dot_location(self, _delta_t):
        if not self.enabled:
            return
        dot = self.game.entities_by_id['dot']
        proj_times_view = self.game.projection * self.game.camera.view_matrix()

        for mesh in self.parent.meshes:
            corners = mesh.corners
            for corner in corners:
                # if not any(x > 2 for x in corner):
                #     continue
                dot.position = corner
                # print(dot.position)
                transformation_matrix = proj_times_view * dot.generate_model_mat()
                dot.shader_program.set_trans_mat(transformation_matrix)
                dot.draw()
