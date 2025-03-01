pipeline {
    agent any
    environment {
        GITHUB_USERNAME="emmaliaocode"
        REPOSITORY_NAME="rstudio-operator"
        WORKFLOW_FILE_NAME="test-python-dispatch.yaml"
        GITHUB_ACCESS_TOKEN=credentials("GITHUB_ACCESS_TOKEN")
        BRANCH_NAME="feat/integ-jenkins-to-ci"
    }

    stages {
        stage("Trigger GitHub Actions Workflow") {
            steps {
                script {
                    try {
                        def url = "https://api.github.com/repos/${GITHUB_USERNAME}/${REPOSITORY_NAME}/actions/workflows/${WORKFLOW_FILE_NAME}/dispatches"
                        def response = sh(script: """
                            curl -X POST \\
                            -H "Accept: application/vnd.github.v3+json" \\
                            -H "Authorization: token ${GITHUB_ACCESS_TOKEN}" \\
                            -d '{"ref": "${BRANCH_NAME}"}' \\
                            "${url}"
                        """, returnStdout: true).trim()
                        if (response){
                            def jsonSlurper = new groovy.json.JsonSlurper()
                            def parsedResponse = jsonSlurper.parseText(response)
                            if (parsedResponse.status != 200) {
                                echo "Failed to trigger Github Action Workflow: ${parsedResponse}"
                                currentBuild.result = "FAILURE"
                            }
                        }
                    } catch (Exception e) {
                        echo "Failed to trigger GitHub Actions Workflow: ${e.getMessage()}"
                        currentBuild.result = "FAILURE"
                    }
                }
            }
        }
    }
}
