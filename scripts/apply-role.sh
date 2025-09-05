#!/usr/bin/env bash
set -euo pipefail

ROLE_DIR="${1:-}"

if [[ -z "$ROLE_DIR" ]]; then
    echo "Usage: $0 <role-directory>"
    exit 1
fi

ROLE_NAME="$(basename "$ROLE_DIR")"
TRUST="$ROLE_DIR/trust-policy.json"
ATTACH="$ROLE_DIR/attach.json"
INLINE="$ROLE_DIR/inline-policy.json"
ENVFILE=".env"

if [[ ! -f "$TRUST" ]]; then
    echo "✗ Missing trust-policy.json in $ROLE_DIR"
    exit 1
fi

if [[ -f "$ENVFILE" ]]; then
    echo "> Loading env vars from $ENVFILE"
    set -a
    source "$ENVFILE"
    set +a
fi

echo "> Processing role: $ROLE_NAME"

if aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
    echo "> Updating trust-policy"
    aws iam update-assume-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-document "file://$TRUST"
else
    echo "> Creating role"
    aws iam create-role \
        --role-name "$ROLE_NAME" \
        --assume-role-policy-document "file://$TRUST"
fi

if [[ -f "$ATTACH" ]]; then
    echo "> Attaching managed policies from attach.json"
    for arn in $(jq -r '.[]' "$ATTACH"); do
        echo " + $arn"
        aws iam attach-role-policy \
            --role-name "$ROLE_NAME" \
            --policy-arn "$arn" || true
    done
fi

if [[ -f "$INLINE" ]]; then
    echo "> Upserting inline policy"
    POLICY_NAME="${ROLE_NAME}-inline"
    envsubst < "$INLINE" > /tmp/policy.json
    aws iam put-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-name "$POLICY_NAME" \
        --policy-document "file:///tmp/policy.json"
fi

echo "✓ Done with $ROLE_NAME"