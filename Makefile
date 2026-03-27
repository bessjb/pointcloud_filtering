IMAGE_NAME=ros2-open3d
CONTAINER_NAME=ros2-open3d-container
WORKSPACE_DIR=$(PWD)
DATA_DIR=/mnt/Data/datasets/EGH437_Perception

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --rm -it \
		--name $(CONTAINER_NAME) \
		-v $(WORKSPACE_DIR)/src:/ros2_ws/src \
		-v $(DATA_DIR):/ros2_ws/Perception_Data \
		$(IMAGE_NAME)

run-host-net:
	docker run --rm -it \
		--name $(CONTAINER_NAME) \
		--network host \
		-v $(WORKSPACE_DIR)/src:/ros2_ws/src \
		-v $(DATA_DIR):/ros2_ws/Perception_Data \
		$(IMAGE_NAME)

run-x11:
	docker run --rm -it \
		--runtime=nvidia \
		--gpus all \
		--name $(CONTAINER_NAME) \
		--privileged \
		--network host \
		-e DISPLAY=:1 \
		-e XAUTHORITY=$(XAUTHORITY) \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		-v $(WORKSPACE_DIR)/src:/ros2_ws/src \
		-v $(DATA_DIR):/ros2_ws/Perception_Data \
 		-u qtuser \
		$(IMAGE_NAME)


shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash
