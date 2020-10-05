// Fill out your copyright notice in the Description page of Project Settings.


#include "GeraPistaBlueprint.h"

void ULoadDataTable::geradDado() {

	UDataTable* pDataTable = LoadObject<UDataTable>(NULL, UTF8_TO_TCHAR("DataTable'/Game/StarterContent/DataTable/Character.Character'"));
	FString ContextString;
	TArray<FName> RowNames;
	RowNames = pDataTable->GetRowNames();
	for (auto& name : RowNames)
	{
		FDataTableTestData* pRow = pDataTable->FindRow<FDataTableTestData>(name, ContextString);
		if (pRow)
		{
			LogDebug("read by row name --- RowName:%s, x:%f, y:%f, z:%f", *(name.ToString()), pRow->x, *pRow->y, pRow->z);
		}
	}
	for (auto it : pDataTable->GetRowMap())
	{
		FString rowName = (it.Key).ToString();
		FDataTableTestData* pRow = (FDataTableTestData*)it.Value;
		LogDebug("read by traversal --- RowName:%s, x:%f, y:%f, z:%f", *rowName, pRow->x, *pRow->y, pRow->z);
	}

}
