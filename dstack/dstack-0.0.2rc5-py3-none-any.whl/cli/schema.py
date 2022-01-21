workflows_schema_yaml = """type: object
properties:
  workflows:
    type: array
    items:
      type: object
      properties:
        name:
          type: string
          minLength: 1
        image:
          type: string
          minLength: 1
        commands:
          type: array
          items:
            type: string
            minLength: 1
          minItems: 1
        depends-on:
          type: object
          additionalProperties: false
          properties:
            repo:
              type: object
              properties:
                include:
                  type: array
                  items:
                    type: string
                    minLength: 1
                  minItems: 1
            workflows:
              type: array
              items:
                type: string
                minLength: 1
              minItems: 1
        artifacts:
          type: array
          items:
            type: string
            minLength: 1
          minItems: 1
        resources:
          type: object
          properties:
            cpu:
              type: object
              properties:
                count:
                  type: integer
                  minimum: 1
              required:
                - count
            memory:
              type: string
              minLength: 1
            gpu:
              type: object
              properties:
                count:
                  type: integer
                  minimum: 1
                name: 
                  type: string
                  minLength: 1
                memory:
                  type: string
                  minLength: 1
              required:
                - count
      additionalProperties: false
      required:
        - name
        - image
        - commands
additionalProperties: false
required:
  - workflows"""