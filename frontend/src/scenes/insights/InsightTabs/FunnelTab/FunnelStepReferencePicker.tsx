import React from 'react'
import { Select } from 'antd'
import { useActions, useValues } from 'kea'
import { funnelLogic } from 'scenes/funnels/funnelLogic'
import { PercentageOutlined } from '@ant-design/icons'

export enum FunnelStepReference {
    total = 'total',
    previous = 'previous',
}

export function FunnelStepReferencePicker(): JSX.Element {
    const { stepReference } = useValues(funnelLogic)
    const { setStepReference } = useActions(funnelLogic)
    const options = [
        {
            value: FunnelStepReference.total,
            icon: <PercentageOutlined />,
            label: 'Overall conversion',
        },
        {
            value: FunnelStepReference.previous,
            icon: <PercentageOutlined />,
            label: 'Relative to previous step',
        },
    ]

    return (
        <Select
            defaultValue={FunnelStepReference.total}
            value={stepReference || FunnelStepReference.total}
            onChange={setStepReference}
            bordered={false}
            dropdownMatchSelectWidth={false}
            data-attr="funnel-step-reference-selector"
            optionLabelProp="label"
        >
            {options.map((option) => (
                <Select.Option
                    key={option.value}
                    value={option.value}
                    label={
                        <>
                            {option.icon} {option.label}
                        </>
                    }
                >
                    {option.label}
                </Select.Option>
            ))}
        </Select>
    )
}
